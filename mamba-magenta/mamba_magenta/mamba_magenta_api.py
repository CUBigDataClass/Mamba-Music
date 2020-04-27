from sandbox import (
    generate_mm_music
)


if __name__ == '__main__':
    music_dict = {
        'temperature': 1.0,
        'length': 1.0,
        'artist': 'music_transformer',
        'genre': 'wild_card',
        'num_generations': 2
    }
    generate_mm_music(music_dict)
"""
['melody_rnn', 'performance_rnn', 'polyphony_rnn',
               'pianoroll_rnn_nade', 'improv_rnn', 'music_vae',
               'music_transformer']

"""