from midi2audio import FluidSynth

import numpy as np
import os
import yaml
import argparse

from magenta.music.protobuf import generator_pb2, music_pb2
from magenta.models.shared import sequence_generator_bundle
import magenta.music as mm
import utils
import uuid


class MambaMagentaModel():
    """
    Base class for all Mamba Models.
    """
    def __init__(self, args, info=None, is_empty_model=False):
        """
        """
        # loads from argparseconfig
        """
        if the user wants to load from a yaml file,
        it takes priority over loading via argparse args.
        """
        if is_empty_model:
            pass
        elif info is not None:
            # info will be a dict with the essential information
            self.temperature = info['temperature']
            self.sequence = info['sequence']
            self.num_steps = info['num_steps']

        elif args.load_config:
            self.midis = self.parse_yaml(args.config_dir, args.config_file)
        else:
            # load from argparse
            self.midis = self.parse_notes_string(args.notes)
        # parse midis or notes for a sequence config
        # convert midi data to sequences that magenta can read.
        if info is None and is_empty_model is False:
            self.convert_to_sequence()
        self.counter = 0

    def convert_mp3(self, filename, to_mp3=True):
        """
        converts midi to mp3.

        Arguments
        ---------
        `filename`: `str`

        `to_mp3`: `bool`
        """
        fs = FluidSynth()
        title = filename.split('.')[0]
        audio_filename = f'{title}.mp3' if to_mp3 else f'{title}.wav'
        # saves file to disk
        fs.midi_to_audio(filename, audio_filename)

    def convert_to_sequence(self):
        """
        converts, from the config file, a sequence to parse.
        """
        self.sequence = music_pb2.NoteSequence()
        for row in self.midis:
            midi_num = int(row[0])
            velocity = int(row[3])
            self.sequence.notes.add(pitch=midi_num, start_time=row[1], end_time=row[2], velocity=velocity)
        self.sequence.total_time = self.time

        self.sequence.tempos.add(qpm=self.tempo)

    def sequence2mid(self):
        if hasattr(self, 'sequence'):
            mm.sequence_proto_to_midi_file(self.sequence, 'model.mid')
        else:
            print("No sequence exists.")

    def get_standard_model(self, model_string, model_filename, options):
        """
        Gets the standard model.
        """
        if model_string not in options:
            raise ValueError(f"Wrong model string provided. Choose from {options}.")
        else:
            os.chdir("models")
            if os.path.isfile(f"{model_filename}.mag"):
                print("mag file already exists!")
            else:
                os.system(f"wget http://download.magenta.tensorflow.org/models/{model_filename}.mag")
            self.model_name = model_filename
            os.chdir("..")

    def initialize(self, name, sequence_generator, extra_name=None):
        """
        Initializes the standard model.
        """
        print(f"Initializing {name}...")
        bundle = sequence_generator_bundle.read_bundle_file(os.path.join(os.getcwd(), "models", f"{self.model_name}.mag"))

        generator_map = sequence_generator.get_generator_map()
        if extra_name is not None:
            self.model_name = extra_name
        self.model = generator_map[self.model_name](checkpoint=None, bundle=bundle)

        self.model.initialize()

    def generate(self, num_steps=128, temperature=1.0,
                 steps_per_second_avail=False, empty=False):
        """
        generates a song.
        """
        if hasattr(self, 'num_steps'):
            num_steps = self.num_steps
        if hasattr(self, 'temperature'):
            temperature = self.temperature

        input_sequence = self.sequence

        if empty:
            input_sequence = music_pb2.NoteSequence()
            input_sequence.tempos.add(qpm=80)

        qpm = input_sequence.tempos[0].qpm
        if steps_per_second_avail:
            steps_per_quarter = int(self.model.steps_per_second * (1 /(qpm / 60)))
            seconds_per_step = 1 / self.model.steps_per_second
        else:
            seconds_per_step = 60.0 / qpm / self.model.steps_per_quarter
            steps_per_quarter = self.model.steps_per_quarter
        quantized_sequence = mm.quantize_note_sequence(input_sequence, steps_per_quarter)

        last_end_time = (max(n.end_time for n in input_sequence.notes)
                         if input_sequence.notes else 0)

        primer_sequence_steps = quantized_sequence.total_quantized_steps
        if primer_sequence_steps > num_steps:
            # easier to make num_steps bigger to accommodate for sizes
            # 4 times the size of original sequence..
            num_steps = primer_sequence_steps * 4

        total_seconds = num_steps * seconds_per_step
        input_sequence.total_time = min(total_seconds, input_sequence.total_time)
        generator_options = generator_pb2.GeneratorOptions()

        generator_options.args['temperature'].float_value = temperature
        generate_section = generator_options.generate_sections.add(
            start_time=last_end_time + seconds_per_step,
            end_time=total_seconds)

        self.output_sequence = self.model.generate(input_sequence, generator_options)
        unique_id = str(uuid.uuid1())
        utils.generated_sequence_2_mp3(self.output_sequence, f"{self.model_name}{unique_id}", use_salamander=True)

    def change_info(self, info, is_empty_model=False):
        """
        changes info dictionary with primer sequence
        """
        if is_empty_model:
            # don't do anything here
            pass
        else:
            # info will be a dict with the essential information
            self.temperature = info['temperature']
            self.sequence = info['sequence']
            self.num_steps = info['num_steps']

    def parse_yaml(self, config_dir, config_filename):
        """
        parses yaml file.
        """
        filepath = os.path.join(config_dir, config_filename)
        try:
            with open(filepath) as file:
                sequence_config = yaml.load(file, Loader=yaml.FullLoader)
                # parse yaml files a bit more here
        except Exception:
            print(f'File {filepath} not found. Resorting to default sequence.')
            self.sequence_config = None
        try:
            self.assert_keys(sequence_config, ['time', 'tempo', 'midis', 'starts', 'ends', 'velocities'])
            self.assert_key_is_list(sequence_config, ['midis', 'starts', 'ends', 'velocities'])
            self.tempo = int(sequence_config['tempo'])
            self.time = float(sequence_config['time'])
            notes_num = len(sequence_config['midis'])
            midis = np.zeros((notes_num, 4))
            for i in range(len(sequence_config['midis'])):
                midis[i, 0] = sequence_config['midis'][i]
                midis[i, 1] = sequence_config['starts'][i]
                midis[i, 2] = sequence_config['ends'][i]
                midis[i, 3] = sequence_config['velocities'][i]
            return midis
        except Exception as e:
            print(f"Error parsing dictionary: {e}")

    def parse_notes_string(self, notes_string):
        """
        parses a string of notes taken via argparse.
        """
        split_notes = notes_string.split()
        midis = []
        # pitch=60, start_time=0.0, end_time=0.5, velocity=80
        running_time = 0.
        for note in split_notes:
            try:
                midi_val = int(note)
                # fill in start time, end time, and velocity as well
                midis.append((midi_val, running_time, running_time + 0.5, 80))
                running_time += 0.5

            except Exception as e:
                print(f'Error reading from note string with exception {e}')
                print("""Default format is "x1, x2, x3 ... xn"
                        Where xn is a midi number between 0 and 128.""")
                raise e
        # defaults for tempo - time is based on amount of notes provided
        self.tempo = 60
        self.time = running_time
        return np.array(midis)

    def assert_keys(self, dictionary, desired_keys):
        for key in desired_keys:
            assert key in dictionary, f'{key} needs to be provided!'

    def assert_key_is_list(self, dictionary, desired_keys):
        """
        Ensures that the desired_keys in a dictionary are all lists,
        and also have the same length.
        """
        running_length = None
        for key in desired_keys:
            assert type(dictionary[key]) == list, "key-pair does not form a list!"
            if running_length is None:
                running_length = len(dictionary[key])
            assert len(dictionary[key]) == running_length, "List lengths must match."
            running_length = len(dictionary[key])
