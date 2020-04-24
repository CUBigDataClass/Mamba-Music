from models import (
    MelodyRNN,
    PerformanceRNN,
    PolyphonyRNN,
    ImprovRNN,
    PianoRollRNNNade,
    MusicVAE,
    MusicTransformer
)
from lakh import LakhDataset
import numpy as np
import magenta.music as mm

# artist 2 actual model
# ARTIST2MODEL = {
#     'Melody': MelodyRNN,
#     'Performance': PerformanceRNN,
#     'Polyphony': PolyphonyRNN,
#     'Improv': ImprovRNN,
#     'PianoRollNade': PianoRollRNNNade,
#     'MusicVAE': MusicVAE,
#     'MusicTransformer': MusicTransformer
# }


def dict_2_note_seq(music_dict):
    """
    converts a dictionary (was originally json)
    into a note sequence for later use.

    structure of json:
    {
        'artist': str
        'tempo': int
        'temperature': int
        'genre': str
        'velocity_variance': int
        'num_steps': int
    }
    """
    ordered_keys = sorted(list(music_dict.keys()))
    validate_info(music_dict, ordered_keys,
                  [str, str, float, int, float, float])
    artist = music_dict['artist']

    # if artist not in ARTIST2MODEL.keys():
    #     keys2list = list(ARTIST2MODEL.keys())
    #     raise KeyError(f'{artist} not in {keys2list}.')
    # model = ARTIST2MODEL[artist]


"""
structure of json:

{

    'artist': str
    'tempo': int
    'temperature': int
    'genre': str
    'tempo': int
    'velocity_variance': int
    'num_steps': int
}
Genre is the most important aspect of this message. It isn't directly
fed into the model, but affects the instrumentation and chordal structure.
Some artists are lacking than others in the ability for variation, especially
polyphonyrnn
"""


def validate_info(info_dict, keys, types_list):
    for idx, key in enumerate(keys):
        if type(info_dict[key]) != types_list[idx]:
            raise TypeError(f'Incorrect type provided for key {key}.')


if __name__ == '__main__':
    dataset = LakhDataset(already_scraped=True)
    genres = dataset.genres
    music_dict = {
        'tempo': 80.0,
        'temperature': 1.0,
        'genre': 'noob',
        'num_steps': 128,
        'velocity_variance': 0.5
    }
    print(dataset[genres[0]])
    midi_file = np.random.choice(dataset[genres[0]])
    print(midi_file)
    seq = mm.midi_file_to_note_sequence(midi_file)
    subseq = mm.extract_subsequence(seq, 0.0, min(20, seq.total_time))
    music_dict['sequence'] = subseq
    model = MelodyRNN(None, info=music_dict)
    # music_dict = {
    #     'artist': 'MelodyRNN'
    # }
    # dict_2_note_seq(None)
