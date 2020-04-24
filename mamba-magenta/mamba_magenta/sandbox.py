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
    print(model_string)
    if model_string == "melody_rnn" or model_string == "performance_rnn":
        subsequence = mm.extract_subsequence(sequence, 0.0, 14.0)
        for note in subsequence.notes:
            # rnns can work with piano data.
            note.program = 0
            note.instrument = 1
        music_dict['sequence'] = subsequence
        if model_string == "performance_rnn":
            music_dict['num_steps'] = 2560

    elif model_string == "polyphony_rnn":
        subsequence = mm.extract_subsequence(sequence, 0.0, 30.0)
        for note in subsequence.notes:
            # rnns can work with piano data.
            note.program = 0
            note.instrument = 1
        music_dict['sequence'] = subsequence
    elif model_string == "pianoroll_rnn_nade":
        subsequence = mm.extract_subsequence(sequence, 0.0, 30.0)
        for note in subsequence.notes:
            # rnns can work with piano data.
            note.program = 0
            note.instrument = 1
        music_dict['sequence'] = subsequence
    elif model_string == "improv_rnn":
        subsequence = mm.extract_subsequence(sequence, 0.0, 30.0)
        melody = mm.infer_melody_for_sequence(subsequence)
        twinkle_twinkle = music_pb2.NoteSequence()
        new_sequence = music_pb2.NoteSequence()
        val = 0.
        for note in subsequence.notes:
            # rnns can work with piano data.
            if note.instrument == melody:
                start = note.start_time
                end = note.end_time
                diff = end - start
                new_sequence.notes.add(pitch=note.pitch, start_time=val, end_time=val+diff, velocity=80)
                val+=diff
            note.program = 0
            note.instrument = 1
        new_sequence.total_time = val
        new_sequence.tempos.add(qpm=subsequence.tempos[0].qpm)
        print(new_sequence.notes)
        # twinkle_twinkle.notes.add(pitch=60, start_time=0.0, end_time=0.5, velocity=80)
        # twinkle_twinkle.notes.add(pitch=60, start_time=0.5, end_time=1.0, velocity=80)
        # twinkle_twinkle.notes.add(pitch=67, start_time=1.0, end_time=1.5, velocity=80)
        # twinkle_twinkle.notes.add(pitch=67, start_time=1.5, end_time=2.0, velocity=80)
        # twinkle_twinkle.notes.add(pitch=69, start_time=2.0, end_time=2.5, velocity=80)
        # twinkle_twinkle.notes.add(pitch=69, start_time=2.5, end_time=3.0, velocity=80)
        # twinkle_twinkle.notes.add(pitch=67, start_time=3.0, end_time=4.0, velocity=80)
        # twinkle_twinkle.notes.add(pitch=65, start_time=4.0, end_time=4.5, velocity=80)
        # twinkle_twinkle.notes.add(pitch=65, start_time=4.5, end_time=5.0, velocity=80)
        # twinkle_twinkle.notes.add(pitch=64, start_time=5.0, end_time=5.5, velocity=80)
        # twinkle_twinkle.notes.add(pitch=64, start_time=5.5, end_time=6.0, velocity=80)
        # twinkle_twinkle.notes.add(pitch=62, start_time=6.0, end_time=6.5, velocity=80)
        # twinkle_twinkle.notes.add(pitch=62, start_time=6.5, end_time=7.0, velocity=80)
        # twinkle_twinkle.notes.add(pitch=60, start_time=7.0, end_time=8.0, velocity=80) 
        # twinkle_twinkle.total_time = 8

        # # 60 bpm!
        # twinkle_twinkle.tempos.add(qpm=60)

        music_dict['sequence'] = new_sequence
    elif model_string == "music_vae":
        pass
    elif model_string == "music_transformer":
        pass
    return music_dict


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
        'num_steps': 2560,
        'velocity_variance': 0.5
    }
    midi_file = np.random.choice(dataset[genres[10]])
    music_dict = render_sequence_to_music_dict(midi_file, "improv_rnn")

    model = ImprovRNN(None, info=music_dict, chords="A C E F Gm")
    try:
        model.generate()
    except Exception as e:
        print(e)
        model.generate()
