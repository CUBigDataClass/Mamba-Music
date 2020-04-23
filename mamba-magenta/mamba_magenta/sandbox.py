from models import (
    MelodyRNN,
    PerformanceRNN,
    PolyphonyRNN,
    ImprovRNN,
    PianoRollRNNNade,
    MusicVAE,
    MusicTransformer
)

# artist 2 actual model
ARTIST2MODEL = {
    'Melody': MelodyRNN,
    'Performance': PerformanceRNN,
    'Polyphony': PolyphonyRNN,
    'Improv': ImprovRNN,
    'PianoRollNade': PianoRollRNNNade,
    'MusicVAE': MusicVAE,
    'MusicTransformer': MusicTransformer
}


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
        'tempo': int
        'velocity_variance': int
        'num_steps': int
    }
    """
    ordered_keys = sorted(list(music_dict.keys()))
    validate_info(music_dict, ordered_keys,
                  [str, str, float, int, float, float])
    artist = music_dict['artist']

    if artist not in ARTIST2MODEL.keys():
        keys2list = list(ARTIST2MODEL.keys())
        raise KeyError(f'{artist} not in {keys2list}.')
    model = ARTIST2MODEL[artist]


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
