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

from magenta.music.protobuf import music_pb2


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


def render_sequence_to_music_dict(midi_file, model_string="melody_rnn"):
    sequence = mm.midi_file_to_note_sequence(midi_file)
    music_dict = {
        'tempo': 80.0,
        'temperature': 1.0,
        'num_steps': 2560,
        'velocity_variance': 0.5
    }
    backup_sequence = None
    basic_models = ["melody_rnn", "performance_rnn", "polyphony_rnn",
                    "pianoroll_rnn_nade"]
    if model_string in basic_models:
        subsequence = mm.extract_subsequence(sequence, 0.0, 14.0)
        for note in subsequence.notes:
            # rnns can work with piano data.
            note.program = 0
            note.instrument = 1
        music_dict['sequence'] = subsequence
        if model_string == "performance_rnn":
            music_dict['num_steps'] = 2560

    elif model_string == "improv_rnn":
        subsequence = mm.extract_subsequence(sequence, 0.0, 30.0)
        melody = mm.infer_melody_for_sequence(subsequence)

        new_sequence = music_pb2.NoteSequence()
        backup_sequence = music_pb2.NoteSequence()
        new_val = 0.
        backup_val = 0.
        for note in subsequence.notes:
            # rnns can work with piano data.
            if note.instrument == melody:
                start = note.start_time
                end = note.end_time
                diff = end - start

                new_sequence.notes.add(pitch=note.pitch, start_time=new_val, end_time=new_val+diff, velocity=160)
                backup_sequence.notes.add(pitch=note.pitch, start_time=backup_val, end_time=backup_val+0.5, velocity=160)

                new_val += diff
                backup_val += 0.5
            note.program = 0
            note.instrument = 1
        new_sequence.total_time = new_val
        new_sequence.tempos.add(qpm=subsequence.tempos[0].qpm)
        backup_sequence.total_time = backup_val
        backup_sequence.tempos.add(qpm=60)
        music_dict['sequence'] = subsequence
        music_dict['backup_sequence'] = backup_sequence

    elif model_string == "music_vae":
        pass
    elif model_string == "music_transformer":
        pass
    return music_dict


def validate_info(info_dict, keys, types_list):
    for idx, key in enumerate(keys):
        if type(info_dict[key]) != types_list[idx]:
            raise TypeError(f'Incorrect type provided for key {key}.')


def create_music(model_string, info):
    """
    creates the music. The real deal.
    """
    basic_models = ["melody_rnn", "performance_rnn", "polyphony_rnn",
                    "pianoroll_rnn_nade"]
    if model_string in basic_models:
        if model_string == "melody_rnn":
            model = MelodyRNN(args=None, info=info)
        elif model_string == "performance_rnn":
            model = PerformanceRNN(args=None, info=info)
        elif model_string == "polyphony_rnn":
            model = PolyphonyRNN(args=None, info=info)
        else:
            # rnn nade model
            model = PianoRollRNNNade(args=None, info=info)
        try:
            model.generate()
        except Exception as e:
            print(e)
            model.generate(empty=True)

    elif model_string == "improv_rnn":
        model = ImprovRNN(None, info=music_dict)
        try:
            model.generate()
        except Exception as e:
            print(e)
            model.generate(backup_seq=music_dict["backup_sequence"])

"""
magenta.models.shared.events_rnn_model.EventSequenceRnnModelError:
primer sequence must be shorter than `num_steps`

"""
if __name__ == '__main__':
    dataset = LakhDataset(already_scraped=True)
    genres = dataset.genres
    # print(genres)
    genre = np.random.choice(genres)
    midi_file = np.random.choice(dataset[genre])
    model_string = "melody_rnn"
    music_dict = render_sequence_to_music_dict(midi_file, model_string)
    # each model needs to be handled differently.
    create_music(model_string, music_dict)
    # model = ImprovRNN(None, info=music_dict, chords="A C E F Gm")
