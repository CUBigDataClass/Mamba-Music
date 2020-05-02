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
import copy


"""
Genre is the most important aspect of this message. It isn't directly
fed into the model, but affects the instrumentation and chordal structure.
Some artists are lacking than others in the ability for variation, especially
polyphonyrnn
"""


def generate_from_best_models(model_string, num_generations, genre):
    """
    generates some really good music from the best models
    """
    if model_string == "music_transformer":
        model = MusicTransformer(genre, is_empty_model=True)
        for i in range(num_generations):
            model.generate()
    else:
        num_chords = len(C.COOL_CHORDS)
        for i in range(num_generations):
            idx = np.random.choice(num_chords)
            chord_selection = C.COOL_CHORDS[idx]
            generate_cool_chords(chord_selection, genre)


def render_sequence_to_music_dict(midi_file, music_dict,
                                  model_string="melody_rnn"):
    sequence = mm.midi_file_to_note_sequence(midi_file)
    # scale to num steps.
    music_dict['num_steps'] = 1024 * music_dict['length']
    backup_sequence = None
    basic_models = ["melody_rnn", "performance_rnn", "polyphony_rnn",
                    "pianoroll_rnn_nade"]
    if model_string in basic_models:
        subsequence = mm.extract_subsequence(sequence, 0.0, C.SUBSEQUENCE_TIME)
        for note in subsequence.notes:
            # rnns can work with piano data.
            note.program = 0
            note.instrument = 1
        music_dict['sequence'] = subsequence
        if model_string == "performance_rnn":
            music_dict['num_steps'] = music_dict['num_steps'] * 4

    elif model_string == "improv_rnn" or model_string == "music_vae":
        subsequence = mm.extract_subsequence(sequence, 0.0, C.SUBSEQUENCE_TIME)
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


def create_music(model_string, infos, num_generations, genre):
    """
    creates the music. The real deal.
    """
    assert len(infos) == num_generations, "Size of infos should be the " \
                                          "same as the number of generations!"
    basic_models = ["melody_rnn", "performance_rnn", "polyphony_rnn",
                    "pianoroll_rnn_nade"]
    except_val = 0
    if model_string in basic_models:
        if model_string == "melody_rnn":
            model = MelodyRNN(genre, info=infos[0])
        elif model_string == "performance_rnn":
            model = PerformanceRNN(genre, info=infos[0])
        elif model_string == "polyphony_rnn":
            model = PolyphonyRNN(genre, info=infos[0])
        else:
            # rnn nade model
            model = PianoRollRNNNade(genre, info=infos[0])
        try:
            model.generate()
            for i in range(1, num_generations):
                except_val += 1
                model.change_info(infos[i])
                model.generate()

        except Exception as e:
            print("ERROR", e)
            for i in range(except_val, num_generations):
                model.generate(empty=True)

    elif model_string == "improv_rnn" or model_string == "music_vae":
        if model_string == "improv_rnn":
            model = ImprovRNN(genre, info=infos[0])
        else:
            model = MusicVAE(genre, info=infos[0], is_conditioned=False)

        try:
            model.generate()
            for i in range(1, num_generations):
                except_val += 1
                model.change_info(infos[i])
                model.generate()

        except Exception as e:
            print("ERROR", e)
            for i in range(except_val, num_generations):
                model.generate(backup_seq=infos[i]["backup_sequence"])

    else:
        # defaults to music transformer variants
        idx = np.random.randint(0, 2)
        if idx == 0:
            model = MusicTransformer(genre, info=infos[0], is_conditioned=True)
            model.generate_basic_notes()
            for i in range(1, num_generations):
                except_val += 1
                model.change_info(infos[i])
                model.generate_basic_notes()
        else:

            try:
                model = MusicTransformer(genre, info=infos[0])
                model.generate_primer()
                for i in range(1, num_generations):
                    except_val += 1

                    model.change_info(infos[i])
                    model.generate_primer()

            except Exception as e:
                print("ERROR", e)
                print("Resorting to unconditioned model here...")
                model = MusicTransformer(genre, is_empty_model=True)
                for i in range(except_val, num_generations):
                    model.generate()


def generate_cool_chords(chord_arr, genre):
    # music vae!
    model = MusicVAE(genre, is_empty_model=True)
    model.generate(chord_arr=chord_arr)


def generate_mm_music(music_dict, main_genre):
    dataset = LakhDataset(already_scraped=True)
    genres = dataset.genres

    if music_dict['genre'] not in (genres + ["wild_card"]):
        genre = np.random.choice(genres)
    else:
        genre = music_dict['genre']

    num_generations = music_dict['num_generations']
    model_string = music_dict['artist']
    if model_string not in C.MODELS_LIST:
        print("Invalid artist. Setting model string to music transformer")

    special_models = ["music_transformer", "music_vae"]
    try:
        if genre == "wild_card" and model_string in special_models:
            # we can generate cool chords only on these conditions.
            generate_from_best_models(model_string, num_generations,
                                      main_genre)

        elif genre == "wild_card" and model_string != "music_vae":
            raise ValueError("Can't use cool chords with other models!")

        else:
            music_dicts = []
            for i in range(num_generations):
                midi_file = np.random.choice(dataset[genre])
                music_dict = render_sequence_to_music_dict(midi_file,
                                                           music_dict,
                                                           model_string)
                music_dicts.append(music_dict)
                music_dict = copy.deepcopy(music_dict)
            create_music(model_string, music_dicts,
                         num_generations, main_genre)

    except Exception as e:
        # if for some reason something fails, give the people what they want.
        # give them the Music Transformer!
        print(e)
        print("---RESORTING TO MUSIC TRANSFORMER---")
        model = MusicTransformer(main_genre, is_empty_model=True)
        model.generate()
