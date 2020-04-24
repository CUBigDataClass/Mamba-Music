import argparse
import magenta.music as mm
from magenta.music.protobuf import music_pb2


from midi2audio import FluidSynth
import os


# from https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def print_progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

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

# def genre_2_sequence(genre):
#     """
#     converts a genre to a basic sequence.
#     """
#     sequence = music_pb2.NoteSequence()
#     if genre == "classical":
#         pass
#     elif genre == "hip-hop  ":
