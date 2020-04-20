from midi2audio import FluidSynth

import numpy as np
import os
import yaml
import argparse

from magenta.music.protobuf import music_pb2
import magenta.music as mm


class MambaMagentaModel():
    """
    Can parse sequence of notes
    """
    def __init__(self, args):
        """
        """
        # loads from argparseconfig
        """
        if the user wants to load from a yaml file,
        it takes priority over loading via argparse args.
        """
        if args.load_config:
            self.midis = self.parse_yaml(args.config_dir, args.config_file)
        else:
            # load from argparse
            self.midis = self.parse_notes_string(args.notes)
        # parse midis or notes for a sequence config
        # convert midi data to sequences that magenta can read.
        self.convert_to_sequence()

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

    def play(self):
        pass

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
                midis.append((midi_val, running_time, running_time+0.5, 80))
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



