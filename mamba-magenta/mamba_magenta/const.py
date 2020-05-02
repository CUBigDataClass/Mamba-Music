import os
VERSION = 1
# artists - 7 models
ARTISTS = ['MelodyRNN', 'PerformanceRNN', 'PolyphonyRNN',
           'PianoRollRNNNade', 'ImprovRNN', 'MusicVAE', 'MusicTransformer']

SPOTIFY_SEARCH_ENDPOINT = 'https://api.spotify.com/v1/search'
SPOTIFY_TOKEN_ENDPOINT = 'https://accounts.spotify.com/api/token'
CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
# a list of cool chords - each chord is transposed 12 steps (octave)
COOL_CHORDS = [['C', 'G', 'Am', 'Em', 'F', 'C', 'F', 'G'], ['Db', 'Ab', 'Bbm', 'Fm', 'Gb', 'Db', 'Gb', 'Ab'], ['D', 'A', 'Bm', 'Gbm', 'G', 'D', 'G', 'A'], ['Eb', 'Bb', 'Cm', 'Gm', 'Ab', 'Eb', 'Ab', 'Bb'], ['E', 'B', 'Dbm', 'Abm', 'A', 'E', 'A', 'B'], ['F', 'C', 'Dm', 'Am', 'Bb', 'F', 'Bb', 'C'], ['Gb', 'Db', 'Ebm', 'Bbm', 'B', 'Gb', 'B', 'Db'], ['G', 'D', 'Em', 'Bm', 'C', 'G', 'C', 'D'], ['Ab', 'Eb', 'Fm', 'Cm', 'Db', 'Ab', 'Db', 'Eb'], ['A', 'E', 'Gbm', 'Dbm', 'D', 'A', 'D', 'E'], ['Bb', 'F', 'Gm', 'Dm', 'Eb', 'Bb', 'Eb', 'F'], ['B', 'Gb', 'Abm', 'Ebm', 'E', 'B', 'E', 'Gb'], ['Dm', 'F', 'Am', 'G'], ['Ebm', 'Gb', 'Bbm', 'Ab'], ['Em', 'G', 'Bm', 'A'], ['Fm', 'Ab', 'Cm', 'Bb'], ['Gbm', 'A', 'Dbm', 'B'], ['Gm', 'Bb', 'Dm', 'C'], ['Abm', 'B', 'Ebm', 'Db'], ['Am', 'C', 'Em', 'D'], ['Bbm', 'Db', 'Fm', 'Eb'], ['Bm', 'D', 'Gbm', 'E'], ['Cm', 'Eb', 'Gm', 'F'], ['Dbm', 'E', 'Abm', 'Gb'], ['C', 'F', 'G'], ['Db', 'Gb', 'Ab'], ['D', 'G', 'A'], ['Eb', 'Ab', 'Bb'], ['E', 'A', 'B'], ['F', 'Bb', 'C'], ['Gb', 'B', 'Db'], ['G', 'C', 'D'], ['Ab', 'Db', 'Eb'], ['A', 'D', 'E'], ['Bb', 'Eb', 'F'], ['B', 'E', 'Gb'], ['Am', 'F', 'C', 'G'], ['Bbm', 'Gb', 'Db', 'Ab'], ['Bm', 'G', 'D', 'A'], ['Cm', 'Ab', 'Eb', 'Bb'], ['Dbm', 'A', 'E', 'B'], ['Dm', 'Bb', 'F', 'C'], ['Ebm', 'B', 'Gb', 'Db'], ['Em', 'C', 'G', 'D'], ['Fm', 'Db', 'Ab', 'Eb'], ['Gbm', 'D', 'A', 'E'], ['Gm', 'Eb', 'Bb', 'F'], ['Abm', 'E', 'B', 'Gb'], ['Am', 'Em', 'G', 'F'], ['Bbm', 'Fm', 'Ab', 'Gb'], ['Bm', 'Gbm', 'A', 'G'], ['Cm', 'Gm', 'Bb', 'Ab'], ['Dbm', 'Abm', 'B', 'A'], ['Dm', 'Am', 'C', 'Bb'], ['Ebm', 'Bbm', 'Db', 'B'], ['Em', 'Bm', 'D', 'C'], ['Fm', 'Cm', 'Eb', 'Db'], ['Gbm', 'Dbm', 'E', 'D'], ['Gm', 'Dm', 'F', 'Eb'], ['Abm', 'Ebm', 'Gb', 'E'], ['F', 'G', 'Am', 'C'], ['Gb', 'Ab', 'Bbm', 'Db'], ['G', 'A', 'Bm', 'D'], ['Ab', 'Bb', 'Cm', 'Eb'], ['A', 'B', 'Dbm', 'E'], ['Bb', 'C', 'Dm', 'F'], ['B', 'Db', 'Ebm', 'Gb'], ['C', 'D', 'Em', 'G'], ['Db', 'Eb', 'Fm', 'Ab'], ['D', 'E', 'Gbm', 'A'], ['Eb', 'F', 'Gm', 'Bb'], ['E', 'Gb', 'Abm', 'B'], ['C', 'Fm', 'Gm'], ['Db', 'Gbm', 'Abm'], ['D', 'Gm', 'Am'], ['Eb', 'Abm', 'Bbm'], ['E', 'Am', 'Bm'], ['F', 'Bbm', 'Cm'], ['Gb', 'Bm', 'Dbm'], ['G', 'Cm', 'Dm'], ['Ab', 'Dbm', 'Ebm'], ['A', 'Dm', 'Em'], ['Bb', 'Ebm', 'Fm'], ['B', 'Em', 'Gbm'], ['D', 'Gm', 'C'], ['Eb', 'Abm', 'Db'], ['E', 'Am', 'D'], ['F', 'Bbm', 'Eb'], ['Gb', 'Bm', 'E'], ['G', 'Cm', 'F'], ['Ab', 'Dbm', 'Gb'], ['A', 'Dm', 'G'], ['Bb', 'Ebm', 'Ab'], ['B', 'Em', 'A'], ['C', 'Fm', 'Bb'], ['Db', 'Gbm', 'B']]
MODELS_LIST = ['melody_rnn', 'performance_rnn', 'polyphony_rnn',
               'pianoroll_rnn_nade', 'improv_rnn', 'music_vae',
               'music_transformer']
SUBSEQUENCE_TIME = 10.0
SONGS_ENDPOINT = 'https://7jeyic96xe.execute-api.us-west-1.amazonaws.com/Prod/Songs'

GENRE_BUCKETS = genres_mapping = {
    'electronic': ['edm', 'dub', 'electronic', 'electropop', 'cover',
                   'techno', 'indietronica', 'house', 'disco',
                   'trance', 'singer-songwriter', 'cristiano', 'cabaret'],
    'jazz/swing': ['blues', 'jazz', 'downtempo', 'motown', 'doo-wop',
                   'funk', 'stride', 'swing', 'soul', 'freakbeat',
                   'gospel', 'bluegrass', 'fusion', 'banda', 'contemporary',
                   'tenor', 'dixieland', 'merseybeat'],
    'folk/world': ['folk', 'zither', 'dansktop', 'volksmusik', 'earth',
                   'country', 'banjo', 'quebecois', 'sleep', 'latin',
                   'listening', 'mexican', 'punta', 'pagode', 'latino',
                   'world', 'flamenco', 'brasileiro', 'caipira',
                   'environmental', 'spytrack', 'paraguaya', 'adoracao',
                   'revival', 'universitario'],
    'rock': ['rock', 'post-rock', 'rock-and-roll',
             'garage', 'gold', 'post-grunge', 'guitar', 'punk',
             'beat', 'anarcho-punk', 'steampunk', 'metal', 'hi-nrg',
             'hardcore', 'storm', 'gabba', 'bass', 'american',
             'americana', 'metalcore', 'rockabilly'],
    'rap': ['rap', 'freestyle', 'trap', 'hop', 'traprun', 'ye', 'beats',
            'urban'],
    'chill': ['chill', 'nova', 'psychill', 'dawn', 'psytrance',
              'reggae', 'r&b', 'flow', 'mellow'],
    'misc': ['indie', 'shaabi', 'levenslied', 'zillertal',
             'karneval', 'yodeling', 'novelty', 'sound', 'mezmur',
             'enfants', 'ska', 'age', 'cv', 'music', 'schlager',
             "d'autore", 'advocacy', 'invasion', 'comic', 'liedermacher',
             'chanson', 'lilith', 'alley', 'standards'],
    'romantic': ['broadway', 'romanticism', 'piano', 'instrumental',
                 'soundtrack', 'romantico', 'show', 'disney',
                 'idol', 'ragtime', 'cappella'],
    'pop': ['synthpop', 'pop', 'post-disco', 'eurodance',
            'era', 'dance', 'austropop', 'nederpop', 'tunes',
            'europop', 'britpop', 'metropopolis'],
    'classical': ['orchestra', 'classical', 'organ', 'band', 'monastic',
                  'quartet', 'hollywood', 'worship']
}