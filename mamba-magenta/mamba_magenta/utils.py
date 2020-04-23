import argparse
import magenta.music as mm

from midi2audio import FluidSynth
import os


def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument Parse for Mamba Magenta Models.')
    parser.add_argument('-m', '--model', type=str, default='melody-rnn',
                        help='Available networks. Choose from:')
    parser.add_argument('-n', '--notes', type=str, default='60 61 62 63',
                        help='Please provide a list of midi notes.')
    parser.add_argument('-lc', '--load_config', type=bool, default=False,
                        help='Whether the config is desired to be used.')
    parser.add_argument('-cfd', '--config_dir', type=str, default='config',
                        help='Config directory')
    parser.add_argument('-cff', '--config_file', type=str, default='sequence.yaml',
                        help='Config file for a note sequence.')

    return parser.parse_args()


def generated_sequence_2_mp3(seq, filename, dirs="songs"):
    """
    generates note sequence `seq` to an mp3 file, with the name
    `filename` in directory(ies) `dir`.
    """
    song_path = os.path.join(dirs, filename)
    # convert from note sequence to midi file.
    mm.sequence_proto_to_midi_file(seq, f'{song_path}.mid')
    fs = FluidSynth()

    fs.midi_to_audio(f'{song_path}.mid', f'{song_path}.mp3')
    # remove midi file for bookkeeping.
    os.remove(f'{song_path}.mid')

def dict_2_note_seq(dict):
    """
    converts a dictionary (was originally json)
    into a note sequence for later use.

    Required keys:

    - 'lol'
    """
    pass


"""
structure of json:

{

    'artist': str
    'tempo': int
    'temperature': int
    'genre': str
    'tempo': int
    'velocity_variance': int
}
Genre is the most important aspect of this message. It isn't directly
fed into the model, but affects the instrumentation and chordal structure.
Some artists are lacking than others in the ability for variation, especially
polyphonyrnn
"""