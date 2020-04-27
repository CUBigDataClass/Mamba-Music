from sandbox import (
    generate_mm_music
)


if __name__ == '__main__':
    music_dict = {
        'temperature': 1.0,
        'length': 1.0,
        'artist': 'music_transformer',
        'genre': 'random',
        'take': 1
    }
    generate_mm_music(music_dict)
