import numpy as np

from sandbox import (
    generate_mm_music
)
import const as C

if __name__ == '__main__':
    music_dict = {
        'temperature': 1.0,
        'length': 1.0,
        'artist': 'music_transformer',
        'genre': 'wild_card',
        'num_generations': 1
    }
    if music_dict['genre'] != 'wild_card':
        if music_dict['genre'] not in list(C.GENRE_BUCKETS.keys()):
            raise KeyError("Genre not found in keys!")

        bucket = C.GENRE_BUCKETS[music_dict['genre']]
        genre = np.random.choice(bucket)
        music_dict['genre'] = genre
    generate_mm_music(music_dict)

"""
names:
['melody_rnn', 'performance_rnn', 'polyphony_rnn',
               'pianoroll_rnn_nade', 'improv_rnn', 'music_vae',
               'music_transformer']

"""
