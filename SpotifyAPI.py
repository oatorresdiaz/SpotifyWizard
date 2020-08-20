from os import environ
import json
import requests
from math import ceil
import numpy
from secret.keys import CLIENT_ID_PUBLIC, CLIENT_ID_SECRET


class SpotifyAPI:

    base_url = 'https://api.spotify.com/v1'

    access_token = None

    refresh_token = None

    def __init__(self):
        if environ.get('IS_HEROKU'):

            self.REDIRECT_URI = 'https://spotify-wizard.herokuapp.com/home'

        else:

            self.REDIRECT_URI = 'http://127.0.0.1:5000/home'

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

        if 'access_token' in request_json and 'refresh_token' in request_json:

            acccess_token = request_json['access_token']

            refresh_token = request_json['refresh_token']

            return acccess_token, refresh_token

        return None, None

    def request_refreshed_access_token(self, refresh_token):

        url = 'https://accounts.spotify.com/api/token'

        data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token, 'client_id': CLIENT_ID_PUBLIC,
                'client_secret': CLIENT_ID_SECRET}

        request = requests.post(url, data=data)

        request_json = json.loads(request.text)

        if 'access_token' in request_json:

            acccess_token = request_json['access_token']

            return acccess_token

        return None

    def search_playlist(self, query):

        url = self.base_url + '/search'

        header = {'Authorization': 'Bearer ' + self.access_token}

        query = query.replace(' ', '+')

        params = {'q': query, 'type': 'playlist', 'limit': '5'}

        request = requests.get(url, headers=header, params=params).json()

        if 'playlists' in request and 'items' in request['playlists']:
            return request['playlists']['items']

        return None

    def get_tracks_from_playlist(self, playlist_id):

        url = self.base_url + '/playlists/' + playlist_id + '/tracks'

        header = {'Authorization': 'Bearer ' + self.access_token}

        request = requests.get(url, headers=header).json()

        tracks = []

        if 'items' in request:

            for item in request['items']:

                if 'track' in item and item['track'] is not None:

                    tracks.append(item['track'])

        return tracks

    def get_tracks_by_ids(self, ids):

        if ids is None or len(ids) == 0:

            return []

        if self.access_token is None:

            access_token = self.request_refreshed_access_token(self.refresh_token)

            self.set_access_token(access_token)

        url = self.base_url + '/tracks'

        header = {'Authorization': 'Bearer ' + self.access_token}

        num_of_parts = ceil(len(ids)/50)

        chunks = numpy.array_split(ids, num_of_parts)

        request = {}

        for ids in chunks:

            ids = ','.join(map(str, ids))

            params = {'ids': ids}

            request = requests.get(url, headers=header, params=params).json()

        if 'tracks' in request:
            return request['tracks']

        return []

    def get_audio_features(self, ids):

        url = self.base_url + '/audio-features'

        header = {'Authorization': 'Bearer ' + self.access_token}

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

        header = {'Authorization': 'Bearer ' + self.access_token}

        request = requests.get(url, headers=header).json()

        return request

    def get_user_saved_tracks(self):

        url = self.base_url + '/me/tracks'

        header = {'Authorization': 'Bearer ' + self.access_token}

        params = {'limit': '50'}

        tracks = []

        request = requests.get(url, headers=header, params=params).json()

        if 'items' in request:
            for track in request['items']:
                if 'track' in track:
                    tracks.append(track['track'])

        # while True:
        #
        #     request = requests.get(url, headers=header, params=params).json()
        #
        #     if 'items' in request:
        #         for track in request['items']:
        #             if 'track' in track:
        #                 tracks.append(track['track'])
        #
        #     if 'next' in request and request['next'] is not None:
        #         url = request['next']
        #     else:
        #         break

        return tracks

    def get_access_token(self):

        return self.access_token

    def get_refresh_token(self):

        return self.refresh_token

    def set_access_token(self, token):

        self.access_token = token

    def set_refresh_token(self, token):

        self.refresh_token = token
