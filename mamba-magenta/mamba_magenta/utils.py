import argparse
import magenta.music as mm
from magenta.music.protobuf import music_pb2


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

def genre_2_sequence(genre):
    """
    converts a genre to a basic sequence.
    """
    sequence = music_pb2.NoteSequence()
    if genre == "classical":
        pass
    elif genre == "hip-hop  ":
#         twinkle_twinkle.notes.add(pitch=60, start_time=0.0, end_time=0.5, velocity=80)
#         twinkle_twinkle.notes.add(pitch=60, start_time=0.5, end_time=1.0, velocity=80)
#         twinkle_twinkle.notes.add(pitch=67, start_time=1.0, end_time=1.5, velocity=80)
#         twinkle_twinkle.notes.add(pitch=67, start_time=1.5, end_time=2.0, velocity=80)
#         twinkle_twinkle.notes.add(pitch=69, start_time=2.0, end_time=2.5, velocity=80)
#         twinkle_twinkle.notes.add(pitch=69, start_time=2.5, end_time=3.0, velocity=80)
#         twinkle_twinkle.notes.add(pitch=67, start_time=3.0, end_time=4.0, velocity=80)
#         twinkle_twinkle.notes.add(pitch=65, start_time=4.0, end_time=4.5, velocity=80)
#         twinkle_twinkle.notes.add(pitch=65, start_time=4.5, end_time=5.0, velocity=80)
#         twinkle_twinkle.notes.add(pitch=64, start_time=5.0, end_time=5.5, velocity=80)
#         twinkle_twinkle.notes.add(pitch=64, start_time=5.5, end_time=6.0, velocity=80)
#         twinkle_twinkle.notes.add(pitch=62, start_time=6.0, end_time=6.5, velocity=80)
#         twinkle_twinkle.notes.add(pitch=62, start_time=6.5, end_time=7.0, velocity=80)
#         twinkle_twinkle.notes.add(pitch=60, start_time=7.0, end_time=8.0, velocity=80) 
#         twinkle_twinkle.total_time = 8

# # 60 bpm!
# twinkle_twinkle.tempos.add(qpm=60)

#     elif genre == "x3":
#         pass
#     elif genre == "x4":
#         pass
#     elif genre == "x5":
#         pass
#     elif genre == "x6":
#         pass
#     elif genre == "x7p":
#         pass
#     elif genre == "x2":
#         pass
#     # mm.s/equn