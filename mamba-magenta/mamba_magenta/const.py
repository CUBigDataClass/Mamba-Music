import os
VERSION = 1
# artists - 7 models
ARTISTS = ['MelodyRNN', 'PerformanceRNN', 'PolyphonyRNN',
           'PianoRollRNNNade', 'ImprovRNN', 'MusicVAE', 'MusicTransformer']

SPOTIFY_SEARCH_ENDPOINT = 'https://api.spotify.com/v1/search'
SPOTIFY_TOKEN_ENDPOINT = 'https://accounts.spotify.com/api/token'
CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
