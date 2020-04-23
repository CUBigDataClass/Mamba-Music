import numpy as np
import json
import os
import shutil
import tarfile
import requests
import const as C
# use spotify api to identify artists


def get_cleaned_midis():
    """
    gets cleaned midis of files.
    """
    tarname = 'clean_midi.tar.gz'
    if os.path.isdir(os.path.join(os.getcwd(), 'data/clean_midi')):
        print('MIDI data already exists! Skipping download...')
    else:
        url = 'http://hog.ee.columbia.edu/craffel/lmd/clean_midi.tar.gz'
        # requests.get(url)
        # using wget will show progress of download instead of seeming to hang.
        os.system(f'wget {url}')
        shutil.move(tarname, 'data')
        my_tar = tarfile.open(f'data/{tarname}')
        my_tar.extractall('data/')
        my_tar.close()
        os.remove('data/{tar}')


def get_genres(bearer_auth, artist_name='Beethoven'):
    """
    gets the genre using the spotify api.
    """
    api_link = C.SPOTIFY_SEARCH_ENDPOINT

    params = {'q': artist_name, 'type': 'artist'}
    data = requests.get(api_link, params=params, auth=bearer_auth).json()
    top_entry = data['artists']['items'][0]
    # for future reference, top_entry['name'] is the name of the top result
    return top_entry['genres']


def get_genres_from_folders():
    os.listdir("data/")
    pass


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
    token = os.environ['SPOTIFY_API_TOKEN']
    bearer = BearerAuth(token)
    genres = get_genres(bearer)
    print(genres)
