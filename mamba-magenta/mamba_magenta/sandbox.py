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
import const as C
from magenta.music.protobuf import music_pb2



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
        'num_steps': 2560
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

    elif model_string == "improv_rnn" or model_string == "music_vae":
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
            if model_string == "improv_rnn":
                note.program = 0
                note.instrument = 1
        new_sequence.total_time = new_val
        new_sequence.tempos.add(qpm=subsequence.tempos[0].qpm)
        backup_sequence.total_time = backup_val
        backup_sequence.tempos.add(qpm=60)
        music_dict['sequence'] = subsequence
        music_dict['backup_sequence'] = backup_sequence
    elif model_string == "music_transformer":
        # model generate will take care of things
        music_dict['sequence'] = sequence

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
            model = MelodyRNN(info=info)
        elif model_string == "performance_rnn":
            model = PerformanceRNN(info=info)
        elif model_string == "polyphony_rnn":
            model = PolyphonyRNN(info=info)
        else:
            # rnn nade model
            model = PianoRollRNNNade(info=info)
        try:
            model.generate()
        except Exception as e:
            print(e)
            model.generate(empty=True)

    elif model_string == "improv_rnn" or model_string == "music_vae":
        if model_string == "improv_rnn":
            model = ImprovRNN(info=music_dict)
        else:
            model = MusicVAE(info=music_dict, is_conditioned=False)
        try:
            model.generate()
        except Exception as e:
            print(e)
            model.generate(backup_seq=music_dict["backup_sequence"])

    else:
        # defaults to music transformer variants
        idx = np.random.randint(0, 2)
        if idx == 0:
            model = MusicTransformer(None, is_conditioned=False, info=music_dict)
            model.generate()
        else:
            try:
                model = MusicTransformer(None, is_conditioned=True, info=music_dict)

                # resort to rudimentary 1 of 3 melodies
                model.generate_basic_notes()
                # model = MusicTransformer(None, is_conditioned=False, info=music_dict)
                # model.generate_primer()
            except Exception as e:
                model = MusicTransformer(None, is_conditioned=True, info=music_dict)

                # resort to rudimentary 1 of 3 melodies
                model.generate_basic_notes()


def generate_cool_chords(model_string, chord_arr):
    # music vae!
    model = MusicVAE(is_empty_model=True)
    model.generate(chord_arr=chord_arr)


if __name__ == '__main__':

    dataset = LakhDataset(already_scraped=True)
    genres = dataset.genres  #+ ["cool_chords"]
    genre = np.random.choice(genres)
    # genre = "cool_chords"
    model_string = "music_vae"

    try:
        if genre == "cool_chords" and model_string == "music_vae":
            # we can generate cool chords only on these conditions.
            num_chords = len(C.COOL_CHORDS)
            idx = np.random.choice(num_chords)
            chord_selection = C.COOL_CHORDS[idx]
            generate_cool_chords(model_string, chord_selection)

        elif genre == "cool_chords" and model_string != "music_vae":
            raise ValueError("Can't use cool chords with other models!")

        else:
            # cool_chords not valid

            midi_file = np.random.choice(dataset[genre])
            music_dict = render_sequence_to_music_dict(midi_file, model_string)
            create_music(model_string, music_dict)
    except Exception as e:
        # if for some reason something fails, give the people what they want.
        # give them the Music Transformer!
        print(e)
        print("---RESORTING TO MUSIC TRANSFORMER---")
        model = MusicTransformer(None, is_conditioned=False, is_empty_model=True)
        model.generate()
