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

CHORD_SYMBOL = music_pb2.NoteSequence.TextAnnotation.CHORD_SYMBOL

# Velocity at which to play chord notes when rendering chords.
CHORD_VELOCITY = 50

BATCH_SIZE = 4
Z_SIZE = 512
TOTAL_STEPS = 512
BAR_SECONDS = 2.0
CHORD_DEPTH = 49

SAMPLE_RATE = 44100


class MelodyRNN(MambaMagentaModel):
    def __init__(self, args, model_string="basic"):
        super(MelodyRNN, self).__init__(args)
        options = ["basic", "mono", "lookback", "attention"]

        self.get_standard_model(model_string, f"{model_string}_rnn", options)
        self.initialize("Melody RNN", melody_rnn_sequence_generator)


class PerformanceRNN(MambaMagentaModel):
    def __init__(self, args, model_string="performance_with_dynamics"):
        super(PerformanceRNN, self).__init__(args)
        options = ["performance", "performance_with_dynamics",
                   "performance_with_dynamics_and_modulo_encoding",
                   "density_conditioned_performance_with_dynamics",
                   "pitch_conditioned_performance_with_dynamics",
                   "multiconditioned_performance_with_dynamics"]
        self.get_standard_model(model_string, model_string, options)

        self.initialize("Performance RNN", performance_sequence_generator)


class PolyphonyRNN(MambaMagentaModel):
    def __init__(self, args, model_string="polyphony"):
        super(PolyphonyRNN, self).__init__(args)
        options = ["polyphony"]
        self.get_standard_model(model_string, "polyphony_rnn", options)
        self.model_name = "polyphony_rnn"
        self.initialize("Polyphony RNN", polyphony_sequence_generator, "polyphony")


class PianoRollRNNNade(MambaMagentaModel):
    def __init__(self, args, model_string="pianoroll_rnn_nade"):
        super(PianoRollRNNNade, self).__init__(args)
        options = ["pianoroll_rnn_nade", "pianoroll_rnn_nade-bach"]
        self.get_standard_model(model_string, model_string, options)
        self.initialize("Pianroll RNN Nade", pianoroll_rnn_nade_sequence_generator, "rnn-nade_attn")


class ImprovRNN(MambaMagentaModel):
    def __init__(self, args, chords, model_string="chord_pitches_improv", phrases=4):
        super(ImprovRNN, self).__init__(args)
        options = ["chord_pitches_improv"]
        self.get_standard_model(model_string, model_string, options)
        raw_chords = chords.split()
        repeated_chords = [chord for chord in raw_chords
                           for _ in range(16)] * phrases
        print(repeated_chords)
        self.backing_chords = mm.ChordProgression(repeated_chords)

        # self.initialize()
        self.initialize("Improv RNN", improv_rnn_sequence_generator)

    def generate(self, empty=False):
        """
        different implementation is needed for improv rnn's
        generation function.
        """
        input_sequence = self.sequence
        num_steps = 2560  # change this for shorter or longer sequences
        temperature = 1.0
        # Set the start time to begin on the next step after the last note ends.
        last_end_time = (max(n.end_time for n in input_sequence.notes)
                  if input_sequence.notes else 0)
        qpm = input_sequence.tempos[0].qpm

        chord_sequence = self.backing_chords.to_sequence(sequence_start_time=0.0, qpm=qpm)

        for text_annotation in chord_sequence.text_annotations:
            if text_annotation.annotation_type == CHORD_SYMBOL:
                chord = input_sequence.text_annotations.add()
                chord.CopyFrom(text_annotation)

        seconds_per_step = 60.0 / qpm / self.model.steps_per_quarter
        total_seconds = len(self.backing_chords) * seconds_per_step
        input_sequence.total_time = len(self.backing_chords) * seconds_per_step

        generator_options = generator_pb2.GeneratorOptions()
        generator_options.args['temperature'].float_value = temperature

        generate_section = generator_options.generate_sections.add(
            start_time=last_end_time + seconds_per_step,
            end_time=total_seconds)

        sequence = self.model.generate(input_sequence, generator_options)
        renderer = mm.BasicChordRenderer(velocity=CHORD_VELOCITY)
        renderer.render(sequence)
        generated_sequence_2_mp3(sequence, f"{self.model_name}{self.counter}")


class MusicVAE(MambaMagentaModel):
    """
    Now this is a unique model.
    """
    def __init__(self, args):
        super(MusicVAE, self).__init__(args)
        self.get_model()

        self.initialize()

    def slerp(self, p0, p1, t):
        """
        Spherical linear interpolation in the latent space
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
        config = configs.CONFIG_MAP['hier-multiperf_vel_1bar_med_chords']
        self.model = TrainedModel(
                        config, batch_size=BATCH_SIZE,
                        checkpoint_dir_or_path='models/model_chords_fb64.ckpt')

    def generate(self, empty=False, chords=['C', 'G', 'A', 'E', 'C' 'G'],
                 num_bars=64, temperature=0.2):
        # Interpolation, Repeating Chord Progression

        z1 = np.random.normal(size=[Z_SIZE])
        z2 = np.random.normal(size=[Z_SIZE])
        z = np.array([self.slerp(z1, z2, t)
                    for t in np.linspace(0, 1, num_bars)])

        seqs = [
            self.model.decode(length=TOTAL_STEPS, z=z[i:i+1, :], temperature=temperature,
                        c_input=self.chord_encoding(chords[i % 4]))[0]
            for i in range(num_bars)
        ]

        self.fix_instruments_for_concatenation(seqs)
        prog_ns = concatenate_sequences(seqs)
        generated_sequence_2_mp3(prog_ns, f"{self.model_name}{self.counter}")


class PianoPerformanceLanguageModelProblem(score2perf.Score2PerfProblem):
    @property
    def add_eos_symbol(self):
        return True


class MusicTransformer(MambaMagentaModel):
    def __init__(self, args):
        super(MusicTransformer, self).__init__(args)
        self.get_model()

        self.initialize()

    def decode(self, ids, encoder):
        ids = list(ids)
        if text_encoder.EOS_ID in ids:
            ids = ids[:ids.index(text_encoder.EOS_ID)]
        return encoder.decode(ids)

    def get_model(self, model_string="model"):

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

    def initialize(self):
        self.model_name = 'transformer'
        self.hparams_set = 'transformer_tpu'
        self.ckpt_path = 'models/checkpoints/unconditional_model_16.ckpt'

        problem = PianoPerformanceLanguageModelProblem()
        self.unconditional_encoders = problem.get_feature_encoders()

        # Set up HParams.
        hparams = trainer_lib.create_hparams(hparams_set=self.hparams_set)
        trainer_lib.add_problem_hparams(hparams, problem)
        hparams.num_hidden_layers = 16
        hparams.sampling_method = 'random'

        # Set up decoding HParams.
        decode_hparams = decoding.decode_hparams()
        decode_hparams.alpha = 0.0
        decode_hparams.beam_size = 1
        self.targets = []
        self.decode_length = 0
        run_config = trainer_lib.create_run_config(hparams)
        estimator = trainer_lib.create_estimator(
            self.model_name, hparams, run_config,
            decode_hparams=decode_hparams)

        input_fn = decoding.make_input_fn_from_generator(self.input_generator())
        self.unconditional_samples = estimator.predict(
            input_fn, checkpoint_path=self.ckpt_path)
        _ = next(self.unconditional_samples)

    def input_generator(self):
        while True:
            yield {
                'targets': np.array([self.targets], dtype=np.int32),
                'decode_length': np.array(self.decode_length, dtype=np.int32)
            }

    def generate(self, empty=False):
        self.targets = []
        self.decode_length = 1024

        # Generate sample events.
        sample_ids = next(self.unconditional_samples)['outputs']

        # Decode to NoteSequence.
        midi_filename = self.decode(
            sample_ids,
            encoder=self.unconditional_encoders['targets'])
        unconditional_ns = mm.midi_file_to_note_sequence(midi_filename)

        mm.sequence_proto_to_midi_file(unconditional_ns, 'songs/output.mid')
        fs = FluidSynth()
        fs.midi_to_audio('songs/output.mid', 'songs/output.mp3')

    def generate_primer(self):
        """
        Put something important here.

        """
        filenames = {
            'C major arpeggio': 'models/primers/c_major_arpeggio.mid',
            'C major scale': 'models/primers/c_major_scale.mid',
            'Clair de Lune': 'models/content/primers/clair_de_lune.mid',
        }
        primer = 'C major scale'
        primer_ns = mm.midi_file_to_note_sequence(filenames[primer])
        primer_ns = mm.apply_sustain_control_changes(primer_ns)
        max_primer_seconds = 20
        if primer_ns.total_time > max_primer_seconds:
            print(f'Primer is longer than {max_primer_seconds} seconds, truncating.')
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

        self.targets = self.unconditional_encoders['targets'].encode_note_sequence(
                        primer_ns)
        # Remove the end token from the encoded primer.
        self.targets = self.targets[:-1]
        self.decode_length = max(0, 4096 - len(self.targets))
        if len(self.targets) >= 4096:
            print('Primer has more events than maximum sequence length; nothing will be generated.')
        # Generate sample events.
        sample_ids = next(self.unconditional_samples)['outputs']

        midi_filename = self.decode(
                        sample_ids,
                        encoder=self.unconditional_encoders['targets'])
        ns = mm.midi_file_to_note_sequence(midi_filename)
        # Append continuation to primer.
        continuation_ns = mm.concatenate_sequences([primer_ns, ns])

        mm.sequence_proto_to_midi_file(continuation_ns, 'songs/output.mid')
        fs = FluidSynth()
        fs.midi_to_audio('songs/output.mid', 'songs/output.mp3')

class MelodyToPianoPerformanceProblem(score2perf.AbsoluteMelody2PerfProblem):
    @property
    def add_eos_symbol(self):
        return True


class MelodicMusicTransformer(MambaMagentaModel):
    def __init__(self, args):
        super(MelodicMusicTransformer, self).__init__(args)
        self.get_model()

        self.initialize()

    def decode(self, ids, encoder):
        ids = list(ids)
        if text_encoder.EOS_ID in ids:
            ids = ids[:ids.index(text_encoder.EOS_ID)]
        return encoder.decode(ids)

    def get_model(self, model_string="model"):

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

    def initialize(self):
        self.model_name = 'transformer'
        self.hparams_set = 'transformer_tpu'
        self.ckpt_path = 'models/checkpoints/melody_conditioned_model_16.ckpt'

        problem = MelodyToPianoPerformanceProblem()
        self.melody_conditioned_encoders = problem.get_feature_encoders()


        # Set up HParams.
        hparams = trainer_lib.create_hparams(hparams_set=self.hparams_set)
        trainer_lib.add_problem_hparams(hparams, problem)
        hparams.num_hidden_layers = 16
        hparams.sampling_method = 'random'

        # Set up decoding HParams.
        decode_hparams = decoding.decode_hparams()
        decode_hparams.alpha = 0.0
        decode_hparams.beam_size = 1
        self.inputs = []
        self.decode_length = 0
        run_config = trainer_lib.create_run_config(hparams)
        estimator = trainer_lib.create_estimator(
            self.model_name, hparams, run_config,
            decode_hparams=decode_hparams)

        input_fn = decoding.make_input_fn_from_generator(self.input_generator())
        self.melody_conditioned_samples = estimator.predict(
            input_fn, checkpoint_path=self.ckpt_path)
        _ = next(self.melody_conditioned_samples)

    def input_generator(self):
        while True:
            yield {
                'inputs': np.array([[self.inputs]], dtype=np.int32),
                'targets': np.zeros([1, 0], dtype=np.int32),
                'decode_length': np.array(self.decode_length, dtype=np.int32)
            }

    def generate(self, empty=False):
        event_padding = 2 * [mm.MELODY_NO_EVENT]

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

        melody = 'Twinkle Twinkle Little Star'

        # Use one of the provided melodies.
        events = [event + 12 if event != mm.MELODY_NO_EVENT else event
                  for e in melodies[melody]
                  for event in [e] + event_padding]
        self.inputs = self.melody_conditioned_encoders['inputs'].encode(
            ' '.join(str(e) for e in events))
        melody_ns = mm.Melody(events).to_sequence(qpm=160)

        self.decode_length = 4096
        sample_ids = next(self.melody_conditioned_samples)['outputs']

        # Decode to NoteSequence.
        midi_filename = self.decode(
            sample_ids,
            encoder=self.melody_conditioned_encoders['targets'])
        accompaniment_ns = mm.midi_file_to_note_sequence(midi_filename)


        mm.sequence_proto_to_midi_file(accompaniment_ns, 'songs/output.mid')
        fs = FluidSynth()
        fs.midi_to_audio('songs/output.mid', 'songs/output.mp3')


if __name__ == '__main__':
    args = parse_arguments()
    model = MusicVAE(args)
    model.generate()
