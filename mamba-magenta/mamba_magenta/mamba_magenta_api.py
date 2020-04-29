import numpy as np

from sandbox import (
    generate_mm_music
)
import const as C
from ai_parser import parse_ai_service_arguments

if __name__ == '__main__':
    args = parse_ai_service_arguments()
    music_dict = {
        'temperature': args.temperature,
        'length': args.length,
        'artist': args.artist,
        'genre': args.genre,
        'num_generations': args.numgenerations
    }

    if music_dict['genre'] == 'random':
        keys = list(C.GENRE_BUCKETS.keys())
        genre_selection = np.random.choice(keys)
        music_dict['genre'] = genre_selection

    if music_dict['genre'] != 'wild_card':
        if music_dict['genre'] not in list(C.GENRE_BUCKETS.keys()):
            raise KeyError("Genre not found in keys!")
        main_genre = music_dict['genre']
        bucket = C.GENRE_BUCKETS[music_dict['genre']]
        genre = np.random.choice(bucket)
        music_dict['genre'] = genre
    else:
        main_genre = 'wild_card'
    print(music_dict)
    generate_mm_music(music_dict, main_genre)

"""
names:
['melody_rnn', 'performance_rnn', 'polyphony_rnn',
               'pianoroll_rnn_nade', 'improv_rnn', 'music_vae',
               'music_transformer']

"""
