import json
import requests
from math import ceil
import numpy
from secret.keys import CLIENT_ID_PUBLIC, CLIENT_ID_SECRET


class SpotifyAPI:

    base_url = 'https://api.spotify.com/v1'
    token = ''
    #REDIRECT_URI = 'http://127.0.0.1:5000/home'
    REDIRECT_URI = 'https://spotify-wizard.herokuapp.com/home'

    def authenticate(self):

        url = 'https://accounts.spotify.com/authorize?'

        url += 'client_id=' + CLIENT_ID_PUBLIC

        url += '&response_type=code&'

        url += 'redirect_uri=' + self.REDIRECT_URI

        url += '&scope=user-read-private, user-library-read'

        return url

    def request_access_and_refresh_tokens(self, code):

        url = 'https://accounts.spotify.com/api/token'

        data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': self.REDIRECT_URI,
                  'client_id': CLIENT_ID_PUBLIC, 'client_secret': CLIENT_ID_SECRET}

        request = requests.post(url, data=data)

        request_json = json.loads(request.text)

        acccess_token = request_json['access_token']

        refresh_token = request_json['refresh_token']

        return acccess_token, refresh_token


    def search_playlist(self, query):

        url = self.base_url + '/search'

        header = {'Authorization': 'Bearer ' + self.token}

        query = query.replace(' ', '+')

        params = {'q': query, 'type': 'playlist', 'limit': '5'}

        request = requests.get(url, headers=header, params=params).json()

        if 'playlists' in request and 'items' in request['playlists']:
            return request['playlists']['items']

        return None

    def get_tracks_from_playlist(self, track_id):

        url = self.base_url + '/playlists/' + track_id + '/tracks'

        header = {'Authorization': 'Bearer ' + self.token}

        request = requests.get(url, headers=header).json()

        tracks = []

        if 'items' in request:

            for item in request['items']:

                if 'track' in item:

                    tracks.append(item['track'])

        return tracks

    def get_audio_features(self, ids):

        url = self.base_url + '/audio-features'

        header = {'Authorization': 'Bearer ' + self.token}

        ids = numpy.array(ids)

        chunk_size = ceil(ids.size/50)

        if chunk_size > 0:

            chunks = numpy.array_split(ids, ceil(ids.size/50))

            audio_features = []

            for chunk in chunks:

                ids = ','.join(map(str, chunk))

                params = {'ids': ids}

                request = requests.get(url, headers=header, params=params).json()

                if 'audio_features' in request:
                    for features in request['audio_features']:
                        audio_features.append(features)

            return audio_features

        return []

    def get_user_profile(self):

        url = self.base_url + '/me'

        header = {'Authorization': 'Bearer ' + self.token}

        request = requests.get(url, headers=header).json()

        return request

    def get_user_saved_tracks(self):

        url = self.base_url + '/me/tracks'

        header = {'Authorization': 'Bearer ' + self.token}

        params = {'limit': '50'}

        tracks = []

        while True:

            request = requests.get(url, headers=header, params=params).json()

            if 'items' in request:
                for track in request['items']:
                    if 'track' in track:
                        tracks.append(track['track'])

            if 'next' in request and request['next'] is not None:
                url = request['next']
            else:
                break

        return tracks

    def get_token(self):
        return self.token

    def set_token(self, token):
        self.token = token
