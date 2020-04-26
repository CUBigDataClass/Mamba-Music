import numpy as np
import json
import os
import shutil
import tarfile
import requests
import const as C
import pickle
from utils import print_progress_bar


def get_spotify_bearer_token():
    """
    gets the spotify token.
    The client id and secrets are defined in `const.py`
    and just get the corresponding key from `os.environ`.
    """
    client_id = C.CLIENT_ID
    client_secret = C.CLIENT_SECRET
    grant_type = 'client_credentials'
    body_params = {'grant_type': grant_type}
    get_token_url = C.SPOTIFY_TOKEN_ENDPOINT
    response = requests.post(get_token_url,
                             data=body_params,
                             auth=(client_id, client_secret))

    token_raw = json.loads(response.text)
    token = token_raw["access_token"]
    return token


def get_genres(bearer_auth, artist_name='Beethoven'):
    """
    gets the genre using the spotify api.
    """
    api_link = C.SPOTIFY_SEARCH_ENDPOINT

    params = {'q': artist_name, 'type': 'artist'}
    data = requests.get(api_link, params=params, auth=bearer_auth).json()
    items = data['artists']['items']
    if len(items) != 0:
        top_entry = data['artists']['items'][0]
        # for future reference, top_entry['name'] is the name of the top result
        name = top_entry['name']
        # print(f'Artist: {name} vs {artist_name}')
        return top_entry['genres']
    else:
        return []


class LakhDataset():
    def __init__(self, already_scraped=False):
        token = get_spotify_bearer_token()
        bearer = BearerAuth(token)
        if already_scraped:
            # check to see if the pickle file exists.
            if os.path.isfile('genre_mappings.pickle'):
                self.genre_mappings = pickle.load(open('genre_mappings.pickle', 'rb'))
                self.loaded = True
            else:
                self.loaded = False
        else:
            self.genre_mappings = {}
            self.loaded = False

        self.main_dir = 'data/clean_midi'
        self.get_cleaned_midis()
        self.bearer = bearer

    def __getitem__(self, key):
        return self.genre_mappings[key]

    @property
    def genres(self):
        return list(self.genre_mappings.keys())

    def get_cleaned_midis(self):
        """
        gets cleaned midis of files.
        """
        tarname = 'clean_midi.tar.gz'
        os.makedirs('data', exist_ok=True)
        if os.path.isdir(os.path.join(os.getcwd(), self.main_dir)):
            print('MIDI data already exists! Skipping download...')

        else:
            url = 'http://hog.ee.columbia.edu/craffel/lmd/clean_midi.tar.gz'

            # using wget will show progress of download instead of seeming to hang.
            os.system(f'wget {url}')
            shutil.move(tarname, 'data/')
            my_tar = tarfile.open(f'data/{tarname}')
            my_tar.extractall('data/')
            my_tar.close()
            os.remove(f'data/{tarname}')

    def get_genres_from_folders(self, dir_name='clean_midi'):
        if self.loaded:
            print('Data is already loaded in self.genre_mappings.')
            return
        d = {}
        artist_names = os.listdir(self.main_dir)
        num_names = len(artist_names)
        for idx, name in enumerate(artist_names):
            songs_dir = os.path.join(self.main_dir, name)
            if os.path.isdir(songs_dir):
                songs = os.listdir(songs_dir)
                for i in range(len(songs)):
                    songs[i] = os.path.join(songs_dir, songs[i])

                genres = get_genres(self.bearer, artist_name=name)
                if len(genres) > 0:
                    main_genre = None
                    filled = False

                    for genre in genres:
                        base_genre = genre.split()[-1]
                        if main_genre is None:
                            main_genre = base_genre

                        if base_genre in d.keys():
                            selected_genre = base_genre
                            d[base_genre] = d.get(base_genre, 0) + 1
                            filled = True
                            break

                    if not filled:
                        selected_genre = base_genre
                        d[main_genre] = 1

                self.genre_mappings[selected_genre] = self.genre_mappings.setdefault(selected_genre, []) + songs
                print_progress_bar(idx + 1, num_names, prefix = 'Progress:', suffix = 'Complete', length = 50)
        with open('genre_mappings.pickle', 'wb') as f:
            pickle.dump(self.genre_mappings, f)
        self.loaded = True


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        """
        used during a request.
        """
        r.headers["authorization"] = "Bearer " + self.token
        return r
