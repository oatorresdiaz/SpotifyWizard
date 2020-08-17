from flask import Flask, request, render_template
from SpotifyAPI import SpotifyAPI
from ML import ML

app = Flask(__name__)

spotify_api = SpotifyAPI()

@app.route('/')
def route():

    return render_template("index.html", user_authorized=False)

@app.route('/search_track', methods=['POST'])
def search_track():

    if 'token' in request.form:

        spotify_api.set_token(request.form['token'])

    if 'label' in request.form:

        search_term = request.form['label']

        features, labels = get_training_data(search_term)

        features_random, labels_random = get_training_data('random music')

        features += features_random

        labels += labels_random

        ml = ML()

        model = ml.create_model(features, labels)

        user_saved_tracks = spotify_api.get_user_saved_tracks()

        saved_track_names = []

        ids = []

        for saved_track in user_saved_tracks:

            if 'name' in saved_track:

                saved_track_names.append(saved_track['name'])

            if 'id' in saved_track:

                ids.append(saved_track['id'])

        audio_features = spotify_api.get_audio_features(ids)

        tracks_for_playlist = []

        tracks_for_playlist_names = []

        for feature in audio_features:

            curr_track = user_saved_tracks.pop(0)

            # Note: key & mode are always int
            keys = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                    'instrumentalness', 'liveness', 'valence', 'tempo']

            feature = [feature[key] for key in keys]

            if model.predict([feature]) == search_term:

                tracks_for_playlist.append(curr_track)

                tracks_for_playlist_names.append(curr_track['name'])

        return render_template("index.html", user_authorized=True, search_term=search_term,
                               saved_track_names=saved_track_names,
                               tracks_for_playlist_names=tracks_for_playlist_names,
                               max_len=len(saved_track_names), min_len=len(tracks_for_playlist_names))

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
    app.run()
    #app.run(debug=True, use_debugger=True)


