import numpy as np
import json
import os
import shutil
import tarfile
import requests
import const as C
# use spotify api to identify artists


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


class LokhDataset():
    def __init__(self):
        self.main_dir = 'data/clean_midi'
        self.get_cleaned_midis()

    def get_cleaned_midis(self):
        """
        gets cleaned midis of files.
        """
        tarname = 'clean_midi.tar.gz'
        if os.path.isdir(os.path.join(os.getcwd(), self.main_dir)):
            print('MIDI data already exists! Skipping download...')

        else:
            url = 'http://hog.ee.columbia.edu/craffel/lmd/clean_midi.tar.gz'

            # using wget will show progress of download instead of seeming to hang.
            os.system(f'wget {url}')
            shutil.move(tarname, 'data')
            my_tar = tarfile.open(self.main_dir)
            my_tar.extractall('data/')
            my_tar.close()
            os.remove('data/{tarname}')

    def get_genres_from_folders(self, dir_name='clean_midi'):
        d = {}
        artist_names = os.listdir(self.main_dir)
        for name in artist_names:
            songs_dir = os.path.join(self.main_dir, name)
            if os.path.isdir(songs_dir):
                num_songs = len(os.listdir(os.path.join(self.main_dir, name)))
                genres = get_genres(bearer, artist_name=name)
                if len(genres) > 0:
                    main_genre = None
                    filled = False

                    for genre in genres:
                        base_genre = genre.split()[-1]
                        if main_genre is None:
                            main_genre = base_genre

                        if base_genre in d.keys():
                            d[base_genre] = d.get(base_genre, 0) + 1
                            filled = True
                            break

                    if not filled:
                        d[main_genre] = 1


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        """
        used during a request.
        """
        r.headers["authorization"] = "Bearer " + self.token
        return r


if __name__ == '__main__':
    token = get_spotify_bearer_token()
    bearer = BearerAuth(token)
    genres = get_genres(bearer)
    print(genres)
    data = LokhDataset()
    data.get_genres_from_folders()
