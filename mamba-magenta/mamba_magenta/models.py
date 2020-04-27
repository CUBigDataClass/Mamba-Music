from mamba_magenta_model import MambaMagentaModel
import os

from magenta.models.shared import sequence_generator_bundle
from magenta.music.protobuf import generator_pb2, music_pb2
from utils import parse_arguments, generated_sequence_2_mp3

from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.models.performance_rnn import performance_sequence_generator
from magenta.models.polyphony_rnn import polyphony_sequence_generator
from magenta.models.pianoroll_rnn_nade import pianoroll_rnn_nade_sequence_generator
from magenta.models.improv_rnn import improv_rnn_sequence_generator

import copy

import magenta.music as mm
from midi2audio import FluidSynth

from magenta.music.sequences_lib import concatenate_sequences
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel
import numpy as np

from tensor2tensor import models
from tensor2tensor import problems
from tensor2tensor.data_generators import text_encoder
from tensor2tensor.utils import decoding
from tensor2tensor.utils import trainer_lib

from magenta.models.score2perf import score2perf


import uuid

CHORD_SYMBOL = music_pb2.NoteSequence.TextAnnotation.CHORD_SYMBOL

# Velocity at which to play chord notes when rendering chords.
CHORD_VELOCITY = 80

BATCH_SIZE = 4
Z_SIZE = 512
TOTAL_STEPS = 512
BAR_SECONDS = 2.0
CHORD_DEPTH = 49

SAMPLE_RATE = 44100


class MelodyRNN(MambaMagentaModel):
    """
    MelodyRNN model
    Generates a one line melody
    with the input sequence as a primer.
    """
    def __init__(self, args=None, model_string="basic", info=None):
        super(MelodyRNN, self).__init__(args, info)
        options = ["basic", "mono", "lookback", "attention"]

        self.get_standard_model(model_string, f"{model_string}_rnn", options)
        self.initialize("Melody RNN", melody_rnn_sequence_generator)


class PerformanceRNN(MambaMagentaModel):
    """
    PerformanceRNN model.
    Somewhat akin to a non-noob fiddling on a piano.
    Not super music, just playing around.

    """
    def __init__(self, args=None, model_string="performance_with_dynamics", info=None):
        super(PerformanceRNN, self).__init__(args, info=info)
        options = ["performance", "performance_with_dynamics",
                   "performance_with_dynamics_and_modulo_encoding",
                   "density_conditioned_performance_with_dynamics",
                   "pitch_conditioned_performance_with_dynamics",
                   "multiconditioned_performance_with_dynamics"]
        self.get_standard_model(model_string, model_string, options)

        self.initialize("Performance RNN", performance_sequence_generator)

    def generate(self, empty=False):
        super(PerformanceRNN, self).generate(steps_per_second_avail=True,
                                             empty=empty)


class PolyphonyRNN(MambaMagentaModel):
    """
    Music slightly akin to Bach

    """
    def __init__(self, args=None, model_string="polyphony", info=None):
        super(PolyphonyRNN, self).__init__(args, info=info)
        options = ["polyphony"]
        self.get_standard_model(model_string, "polyphony_rnn", options)
        self.model_name = "polyphony_rnn"
        self.initialize("Polyphony RNN", polyphony_sequence_generator, "polyphony")


class PianoRollRNNNade(MambaMagentaModel):
    """
    A bit of a more intriguing model.
    """
    def __init__(self, args=None, model_string="pianoroll_rnn_nade", info=None):
        super(PianoRollRNNNade, self).__init__(args, info=info)
        options = ["pianoroll_rnn_nade", "pianoroll_rnn_nade-bach"]
        self.get_standard_model(model_string, model_string, options)
        self.initialize("Pianroll RNN Nade", pianoroll_rnn_nade_sequence_generator, "rnn-nade_attn")


class ImprovRNN(MambaMagentaModel):
    """
    improv rnn, which generates melodies underlying a
    specific set of chords.
    Requires both the chords and number of times to repeat those chords
    (can be 1 though).
    """
    def __init__(self, args=None, model_string="chord_pitches_improv",
                 phrase_num=4, info=None, is_empty_model=False):

        super(ImprovRNN, self).__init__(args, info=info,
                                        is_empty_model=is_empty_model)
        options = ["chord_pitches_improv"]
        self.phrase_num = 4
        self.get_standard_model(model_string, model_string, options)

        self.initialize("Improv RNN", improv_rnn_sequence_generator)

    def generate(self, empty=False, backup_seq=None):
        """
        different implementation is needed for improv rnn's
        generation function.
        """
        if backup_seq is not None:
            self.sequence = copy.deepcopy(backup_seq)

        input_sequence = copy.deepcopy(self.sequence)

        num_steps = self.num_steps  # change this for shorter/longer sequences
        temperature = self.temperature
        # Set the start time to begin on the next step after the last note ends.

        last_end_time = (max(n.end_time for n in input_sequence.notes)
                if input_sequence.notes else 0)
        qpm = input_sequence.tempos[0].qpm

        input_sequence = mm.quantize_note_sequence(input_sequence, self.model.steps_per_quarter)
        primer_sequence_steps = input_sequence.total_quantized_steps

        if primer_sequence_steps > num_steps:
            # easier to make num_steps bigger to accommodate for sizes
            # 4 times the size of original sequence..
            num_steps = primer_sequence_steps * 4

        mm.infer_chords_for_sequence(input_sequence)
        raw_chord_string = ""
        for annotation in input_sequence.text_annotations:
            if annotation.annotation_type == CHORD_SYMBOL:
                chord_name = annotation.text
                raw_chord_string += f'{chord_name} '
        raw_chord_string = raw_chord_string[:-1]

        raw_chords = raw_chord_string.split()
        repeated_chords = [chord for chord in raw_chords
                           for _ in range(16)] * self.phrase_num
        self.backing_chords = mm.ChordProgression(repeated_chords)

        chord_sequence = self.backing_chords.to_sequence(sequence_start_time=0.0, qpm=qpm)

        for text_annotation in chord_sequence.text_annotations:
            if text_annotation.annotation_type == CHORD_SYMBOL:
                chord = self.sequence.text_annotations.add()
                chord.CopyFrom(text_annotation)

        seconds_per_step = 60.0 / qpm / self.model.steps_per_quarter

        total_seconds = len(self.backing_chords) * seconds_per_step
        self.sequence.total_time = total_seconds

        generator_options = generator_pb2.GeneratorOptions()
        generator_options.args['temperature'].float_value = temperature

        generate_section = generator_options.generate_sections.add(
            start_time=last_end_time + seconds_per_step,
            end_time=total_seconds)

        sequence = self.model.generate(self.sequence, generator_options)
        renderer = mm.BasicChordRenderer(velocity=CHORD_VELOCITY)
        renderer.render(sequence)
        unique_id = str(uuid.uuid1())
        generated_sequence_2_mp3(sequence, f"{self.model_name}{unique_id}")


class MusicVAE(MambaMagentaModel):
    """
    ## Music Variational Autoencoder
    Paper at: https://arxiv.org/abs/1803.05428

    Now this is a unique model. And definitely the fan favorite.

    """
    def __init__(self, args=None, is_conditioned=True, info=None,
                 is_empty_model=False):
        super(MusicVAE, self).__init__(args, info, is_empty_model=is_empty_model)
        self.get_model()
        self.is_conditioned = is_conditioned
        self.initialize()

    def slerp(self, p0, p1, t):
        """
        Spherical linear interpolation in the latent space, will help decode
        and generate the models later on.
        """
        omega = np.arccos(np.dot(np.squeeze(p0/np.linalg.norm(p0)), np.squeeze(p1/np.linalg.norm(p1))))
        so = np.sin(omega)
        return np.sin((1.0 - t)*omega) / so * p0 + np.sin(t * omega)/so * p1

    def chord_encoding(self, chord):
        index = mm.TriadChordOneHotEncoding().encode_event(chord)
        c = np.zeros([TOTAL_STEPS, CHORD_DEPTH])
        c[0, 0] = 1.0
        c[1:, index] = 1.0
        return c

    def fix_instruments_for_concatenation(self, note_sequences):
        instruments = {}
        for i in range(len(note_sequences)):
            for note in note_sequences[i].notes:
                if not note.is_drum:
                    if note.program not in instruments:
                        if len(instruments) >= 8:
                            instruments[note.program] = len(instruments) + 2
                        else:
                            instruments[note.program] = len(instruments) + 1
                    note.instrument = instruments[note.program]
                else:
                    note.instrument = 9

    def get_model(self, model_string="music_vae"):

        # models folder already exists with this repository.
        os.chdir("models")
        dir_name = os.getcwd()
        files = os.listdir(dir_name)
        expected_files = ['model_fb256.ckpt.index',
                          'model_fb256.ckpt.meta',
                          'model_chords_fb64.ckpt.meta',
                          'model_chords_fb64.ckpt.index',
                          'model_fb256.ckpt.data-00000-of-00001',
                          'model_chords_fb64.ckpt.data-00000-of-00001']

        # if the length of this is 6, no need to redownload checkpoints
        set_len = len(set(files).intersection(set(expected_files)))

        if set_len != 6:
            print("Getting checkpoints. Please wait..")
            os.system(f"gsutil -q -m cp gs://download.magenta.tensorflow.org/models/music_vae/multitrack/* {dir_name}")
            print("Successfully retrieved all checkpoints")
            self.model_name = f"{model_string}"
        else:
            print("Checkpoints already exist in model folder!")
            self.model_name = f"{model_string}"
        os.chdir("..")

    def initialize(self):
        if self.is_conditioned:
            config_string = 'hier-multiperf_vel_1bar_med_chords'
            ckpt_string = 'model_chords_fb64.ckpt'

        else:
            config_string = 'hier-multiperf_vel_1bar_med'
            ckpt_string = 'model_fb256.ckpt'

        config = configs.CONFIG_MAP[config_string]
        self.model = TrainedModel(
                        config, batch_size=BATCH_SIZE,
                        checkpoint_dir_or_path=f'models/{ckpt_string}')

        if not self.is_conditioned:
            self.model._config.data_converter._max_tensors_per_input = None

    def generate(self, empty=False,
                 num_bars=64, temperature=0.5, backup_seq=None,
                 chord_arr=None):
        # Interpolation, Repeating Chord Progression
        if chord_arr is None:
            if backup_seq is not None:
                self.sequence = copy.deepcopy(backup_seq)

            if hasattr(self, 'temperature'):
                temperature = self.temperature
            copy_sequence = copy.deepcopy(self.sequence)

            quantized_sequence = mm.quantize_note_sequence(copy_sequence, 8)
            # infer chords for sequence is a bit more natural
            mm.infer_chords_for_sequence(quantized_sequence)

            chords = []
            for annotation in quantized_sequence.text_annotations:
                if annotation.annotation_type == CHORD_SYMBOL:
                    chord_name = annotation.text
                    chords.append(chord_name)
        else:
            # follow a user defined chord progression
            chords = chord_arr
        mod_val = len(chords)
        z1 = np.random.normal(size=[Z_SIZE])
        z2 = np.random.normal(size=[Z_SIZE])
        z = np.array([self.slerp(z1, z2, t)
                    for t in np.linspace(0, 1, num_bars)])

        seqs = [
            self.model.decode(length=TOTAL_STEPS, z=z[i:i+1, :], temperature=temperature,
                        c_input=self.chord_encoding(chords[i % mod_val]))[0]
            for i in range(num_bars)
        ]

        self.fix_instruments_for_concatenation(seqs)
        prog_ns = concatenate_sequences(seqs)
        unique_id = str(uuid.uuid1())
        generated_sequence_2_mp3(prog_ns, f"{self.model_name}{unique_id}")


    def trim_sequence(self, seq, num_seconds=12.0):
        seq = mm.extract_subsequence(seq, 0.0, num_seconds)
        seq.total_time = num_seconds


class PianoPerformanceLanguageModelProblem(score2perf.Score2PerfProblem):
    @property
    def add_eos_symbol(self):
        return True


class MelodyToPianoPerformanceProblem(score2perf.AbsoluteMelody2PerfProblem):
    @property
    def add_eos_symbol(self):
        return True


class MusicTransformer(MambaMagentaModel):
    """
    Music Transformer model.

    Can be "primed" with a melody, and
    helps provide accompaniment.
    """
    def __init__(self, args=None, is_conditioned=False, info=None,
                 is_empty_model=False):
        super(MusicTransformer, self).__init__(args, info,
                                               is_empty_model=is_empty_model)
        self.get_model()

        self.initialize(is_conditioned)

    def decode(self, ids, encoder):
        ids = list(ids)
        if text_encoder.EOS_ID in ids:
            ids = ids[:ids.index(text_encoder.EOS_ID)]
        return encoder.decode(ids)

    def get_model(self, model_string="music_transformer"):

        # models folder already exists with this repository.
        os.chdir("models")
        dir_name = os.getcwd()
        checkpoints_folder = os.path.join(dir_name, "checkpoints")
        checkpoints_exist = os.path.exists(checkpoints_folder)
        if checkpoints_exist:
            files = os.listdir(checkpoints_folder)
            checkpoint_files = ["melody_conditioned_model_16.ckpt.data-00000-of-00001",
                                "melody_conditioned_model_16.ckpt.index",
                                "melody_conditioned_model_16.ckpt.meta",
                                "unconditional_model_16.ckpt.data-00000-of-00001",
                                "unconditional_model_16.ckpt.index",
                                "unconditional_model_16.ckpt.meta"]
            set_len = len(set(files).intersection(set(checkpoint_files)))

        # if the length of this is 6, no need to redownload checkpoints
        model_found = checkpoints_exist and (set_len == 6)
        if not model_found:
            print("Getting checkpoints. Please wait..")
            os.system(f"gsutil -q -m cp -r gs://magentadata/models/music_transformer/* {dir_name}")
            print("Successfully retrieved all checkpoints")
            self.model_name = f"{model_string}"
        else:
            print("Checkpoints already exist in model folder!")

        os.chdir("..")

    def initialize(self, is_conditioned=False):
        self.model_name = 'transformer'
        self.hparams_set = 'transformer_tpu'
        self.conditioned = is_conditioned
        if self.conditioned:
            self.ckpt_path = 'models/checkpoints/melody_conditioned_model_16.ckpt'
            problem = MelodyToPianoPerformanceProblem()
        else:
            self.ckpt_path = 'models/checkpoints/unconditional_model_16.ckpt'
            problem = PianoPerformanceLanguageModelProblem()

        self.encoders = problem.get_feature_encoders()

        # Set up hyperparams
        hparams = trainer_lib.create_hparams(hparams_set=self.hparams_set)
        trainer_lib.add_problem_hparams(hparams, problem)
        hparams.num_hidden_layers = 16
        hparams.sampling_method = 'random'

        # Set up decoding hyperparams
        decode_hparams = decoding.decode_hparams()
        decode_hparams.alpha = 0.0
        decode_hparams.beam_size = 1
        if self.conditioned:
            self.inputs = []
        else:
            self.targets = []

        self.decode_length = 0
        run_config = trainer_lib.create_run_config(hparams)
        estimator = trainer_lib.create_estimator(
            self.model_name, hparams, run_config,
            decode_hparams=decode_hparams)
        fnc = self.input_generation_conditional if self.conditioned else self.input_generator_unconditional
        input_fn = decoding.make_input_fn_from_generator(fnc())
        self.samples = estimator.predict(
            input_fn, checkpoint_path=self.ckpt_path)
        _ = next(self.samples)

    def input_generation_conditional(self):
        while True:
            yield {
                'inputs': np.array([[self.inputs]], dtype=np.int32),
                'targets': np.zeros([1, 0], dtype=np.int32),
                'decode_length': np.array(self.decode_length, dtype=np.int32)
            }

    def input_generator_unconditional(self):
        while True:
            yield {
                'targets': np.array([self.targets], dtype=np.int32),
                'decode_length': np.array(self.decode_length, dtype=np.int32)
            }

    def failsafe(self):
        melodies = {
                'Mary Had a Little Lamb': [
                    64, 62, 60, 62, 64, 64, 64, mm.MELODY_NO_EVENT,
                    62, 62, 62, mm.MELODY_NO_EVENT,
                    64, 67, 67, mm.MELODY_NO_EVENT,
                    64, 62, 60, 62, 64, 64, 64, 64,
                    62, 62, 64, 62, 60, mm.MELODY_NO_EVENT,
                    mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT
                ],
                'Row Row Row Your Boat': [
                    60, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
                    60, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
                    60, mm.MELODY_NO_EVENT, 62,
                    64, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
                    64, mm.MELODY_NO_EVENT, 62,
                    64, mm.MELODY_NO_EVENT, 65,
                    67, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
                    mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
                    72, 72, 72, 67, 67, 67, 64, 64, 64, 60, 60, 60,
                    67, mm.MELODY_NO_EVENT, 65,
                    64, mm.MELODY_NO_EVENT, 62,
                    60, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
                    mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT
                ],
                'Twinkle Twinkle Little Star': [
                    60, 60, 67, 67, 69, 69, 67, mm.MELODY_NO_EVENT,
                    65, 65, 64, 64, 62, 62, 60, mm.MELODY_NO_EVENT,
                    67, 67, 65, 65, 64, 64, 62, mm.MELODY_NO_EVENT,
                    67, 67, 65, 65, 64, 64, 62, mm.MELODY_NO_EVENT,
                    60, 60, 67, 67, 69, 69, 67, mm.MELODY_NO_EVENT,
                    65, 65, 64, 64, 62, 62, 60, mm.MELODY_NO_EVENT,
                    60, 60, 67, 67, 69, 69, 67, mm.MELODY_NO_EVENT,
                    65, 65, 64, 64, 62, 62, 60, mm.MELODY_NO_EVENT,
                    67, 67, 65, 65, 64, 64, 62, mm.MELODY_NO_EVENT,
                    67, 67, 65, 65, 64, 64, 62, mm.MELODY_NO_EVENT,
                    60, 60, 67, 67, 69, 69, 67, mm.MELODY_NO_EVENT,
                    65, 65, 64, 64, 62, 62, 60, mm.MELODY_NO_EVENT
                ]
            }
        event_padding = 2 * [mm.MELODY_NO_EVENT]

        rand_key = np.random.choice(list(melodies.keys()))

        # Use one of the provided melodies.
        events = [event + 12 if event != mm.MELODY_NO_EVENT else event
                  for e in melodies[rand_key]
                  for event in [e] + event_padding]
        self.inputs = self.encoders['inputs'].encode(
            ' '.join(str(e) for e in events))

    def generate(self):
        # based on i
        self.targets = []
        self.decode_length = 1024

        # Generate sample events.
        sample_ids = next(self.samples)['outputs']
        # Decode to NoteSequence.
        midi_filename = self.decode(
            sample_ids,
            encoder=self.encoders['targets'])
        unconditional_ns = mm.midi_file_to_note_sequence(midi_filename)
        unique_id = str(uuid.uuid1())
        generated_sequence_2_mp3(unconditional_ns, f"{self.model_name}{unique_id}", use_salamander=True)

    def generate_primer(self):
        """
        Put something important here.

        """
        if self.conditioned:
            raise ValueError("Should be using an unconditioned model!")

        primer_ns = self.sequence
        primer_ns = mm.apply_sustain_control_changes(primer_ns)
        max_primer_seconds = 10

        if primer_ns.total_time > max_primer_seconds:
            print(f'Primer is longer than {max_primer_seconds} seconds, truncating.')
            # cut primer if it's too long
            primer_ns = mm.extract_subsequence(
                primer_ns, 0, max_primer_seconds)

        if any(note.is_drum for note in primer_ns.notes):
            print('Primer contains drums; they will be removed.')
            notes = [note for note in primer_ns.notes if not note.is_drum]
            del primer_ns.notes[:]
            primer_ns.notes.extend(notes)

        for note in primer_ns.notes:
            # make into piano
            note.instrument = 1
            note.program = 0

        self.targets = self.encoders['targets'].encode_note_sequence(
                        primer_ns)
        # Remove the end token from the encoded primer.
        self.targets = self.targets[:-1]
        self.decode_length = max(0, 4096 - len(self.targets))

        if len(self.targets) >= 4096:
            print('Primer has more events than maximum sequence length; nothing will be generated.')
        # Generate sample events.
        sample_ids = next(self.samples)['outputs']

        midi_filename = self.decode(
                        sample_ids,
                        encoder=self.encoders['targets'])
        ns = mm.midi_file_to_note_sequence(midi_filename)
        # Append continuation to primer.
        continuation_ns = mm.concatenate_sequences([primer_ns, ns])

        unique_id = str(uuid.uuid1())
        generated_sequence_2_mp3(continuation_ns, f"{self.model_name}{unique_id}", use_salamander=True)

    def generate_basic_notes(self, qpm=160, failsafe=False):
        """
        Requires melody conditioned model.
        """
        if not self.conditioned:
            raise ValueError("Model should be conditioned!")

        if failsafe:
            self.failsafe()

        else:
            melody_ns = copy.deepcopy(self.sequence)
            try:
                melody_instrument = mm.infer_melody_for_sequence(melody_ns)
                notes = [note for note in melody_ns.notes
                        if note.instrument == melody_instrument]

                melody_ns.notes.extend(
                    sorted(notes, key=lambda note: note.start_time))
                for i in range(len(melody_ns.notes) - 1):
                    melody_ns.notes[i].end_time = melody_ns.notes[i + 1].start_time

                # sequence can only be one min to save time during inference.
                melody_ns = mm.extract_subsequence(melody_ns, 0, 60)
                self.inputs = self.encoders['inputs'].encode_note_sequence(
                            melody_ns)
                print("Melody successfully parsed and encoded!")
            except Exception as e:
                print(f"Error in encoding stage {e}")
                print("Resorting to a basic melody")
                self.failsafe()

        self.decode_length = 4096
        sample_ids = next(self.samples)['outputs']

        # Decode to NoteSequence.
        midi_filename = self.decode(
            sample_ids,
            encoder=self.encoders['targets'])
        accompaniment_ns = mm.midi_file_to_note_sequence(midi_filename)

        unique_id = str(uuid.uuid1())
        generated_sequence_2_mp3(accompaniment_ns, f"{self.model_name}{unique_id}", use_salamander=True)
