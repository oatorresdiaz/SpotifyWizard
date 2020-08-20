from os import environ
from flask import Flask, request, render_template, redirect
from SpotifyAPI import SpotifyAPI

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

spotify_api = SpotifyAPI()


@app.route('/')
def route():

    auth_url = spotify_api.authenticate()

    return redirect(auth_url)


@app.route('/home')
def home():

    if spotify_api.get_access_token():  # If there's already a token, get a new one. They expire quickly.

        new_access_token = spotify_api.request_refreshed_access_token(spotify_api.get_refresh_token())

        spotify_api.set_access_token(new_access_token)

    elif 'code' in request.args:  # First time user authorization

        access_token, refresh_token = spotify_api.request_access_and_refresh_tokens(request.args['code'])

        if access_token is not None:

            spotify_api.set_access_token(access_token)

            spotify_api.set_refresh_token(refresh_token)

        else:

            return redirect('/')

    return render_template("index.html", show_results=False)


@app.route('/create_curated_playlist', methods=['POST'])
def create_curated_playlist():

    if 'label' in request.form:

        search_term = request.form['label']

        saved_tracks = spotify_api.get_user_saved_tracks()

        response = {'search_term': search_term.replace(' ', '_')}

        track_meta = []

        for track in saved_tracks:

            if 'preview_url' in track and track['preview_url'] is not None:

                tuple = (track['id'], track['preview_url'])

                track_meta.append(tuple)

        response['track_meta'] = track_meta

        return response

    elif 'curated_playlist_ids' in request.json:

        search_term = request.json['search_term']

        ids = request.json['curated_playlist_ids']

        tracks = spotify_api.get_tracks_by_ids(ids)

        curated_track_names = []

        for track in tracks:

            curated_track_names.append(track['name'])

        return {'search_term': search_term, 'track_names': curated_track_names}


if __name__ == "__main__":
    if environ.get('IS_HEROKU'):
        app.run()
    else:
        app.run(debug=True, use_debugger=True)


