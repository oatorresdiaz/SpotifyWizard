from os import environ
import numpy
import json
import requests
from math import ceil
from flask import Flask, request, render_template, redirect
from SpotifyAPI import SpotifyAPI
from ML import ML

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

spotify_api = SpotifyAPI()


@app.route('/')
def route():

    auth_url = spotify_api.authenticate()

    return redirect(auth_url)


@app.route('/home')
def home():

    if 'code' in request.args:

        access_token, refresh_token = spotify_api.request_access_and_refresh_tokens(request.args['code'])

        if access_token is not None:

            spotify_api.set_token(access_token)

    return render_template("index.html", show_results=False)


@app.route('/create_curated_playlist', methods=['POST'])
def create_curated_playlist():

    if 'label' in request.form:

        search_term = request.form['label']

        if environ.get('IS_HEROKU'):

            url = 'https://spotify-wizard-merlin.herokuapp.com/classify-music'

        else:

            url = 'http://127.0.0.1:5001/classify-music'

        saved_tracks = spotify_api.get_user_saved_tracks()

        dict = {'search_term': search_term.replace(' ', '_')}

        track_meta = []

        for track in saved_tracks:

            if 'preview_url' in track and track['preview_url'] is not None:

                tuple = (track['id'], track['preview_url'])

                track_meta.append(tuple)

        dict['track_meta'] = track_meta

        return dict

    elif 'curated_playlist_ids' in request.json:

        search_term = request.json['search_term']

        ids = request.json['curated_playlist_ids']

        tracks = spotify_api.get_tracks_by_ids(ids)

        curated_track_names = []

        for track in tracks:

            curated_track_names.append(track['name'])

        return {'track_names': curated_track_names}

        # return render_template("index.html", show_results=True, search_term=search_term,
        #                        curated_track_names=curated_track_names,
        #                        curated_tracks_len=len(curated_track_names))


def get_training_data(search_term):

    playlists = spotify_api.search_playlist(search_term)

    features = []

    labels = []

    for playlist in playlists:

        if 'id' in playlist:

            tracks = spotify_api.get_tracks_from_playlist(playlist['id'])

            track_ids = []

            for track in tracks:

                if 'id' in track:
                    track_ids.append(track['id'])

            audio_features = spotify_api.get_audio_features(track_ids)

            for feature in audio_features:

                if feature is None:
                    continue

                # Note: key & mode are always int
                keys = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                        'instrumentalness', 'liveness', 'valence', 'tempo']

                values = [feature[key] for key in keys]

                features.append(values)

                labels.append(search_term)

    return features, labels


if __name__ == "__main__":
    if environ.get('IS_HEROKU'):
        app.run()
    else:
        app.run(debug=True, use_debugger=True)


