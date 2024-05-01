import pandas as pd
from flask import Flask, request, render_template, jsonify
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import webbrowser

app = Flask(__name__)

# Read the CSV file containing the song data
song_data = pd.read_csv('music_data.csv')

# Spotify API credentials
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# Function to get Spotify access token
def get_spotify_access_token():
    request_body = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=request_body)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        return None

# Function to play a song on Spotify
def play_song(track_name):
    access_token = get_spotify_access_token()
    if access_token:
        spotify = spotipy.Spotify(auth=access_token)
        results = spotify.search(q=f'track:{track_name}', type='track')
        if results['tracks']['total'] == 0:
            print("Song not found. Please try again.")
        else:
            track_uri = results['tracks']['items'][0]['uri']
            webbrowser.open(track_uri)
    else:
        print("Failed to get Spotify access token.")

# Function to recommend songs based on hobby
def recommend_songs(hobby):
    # Filter songs based on the selected hobby
    hobby_songs = song_data[song_data['hobbies'] == hobby]
    # Randomly select up to 9 songs from the filtered list
    selected_songs = hobby_songs.sample(min(9, len(hobby_songs)))
    # Return a list of dictionaries containing song information
    return selected_songs[['artist_name', 'track_name', 'year']].to_dict(orient='records')

@app.route('/recommend-songs', methods=['POST'])
def recommend_songs_route():
    selected_hobby = request.form['hobby']
    recommended = recommend_songs(selected_hobby)
    return render_template('hobby_recommendations.html', songs=recommended, hobby=selected_hobby)

# Function to recommend songs based on emotion
def recommend_songs_emotion(emotion):
    # Filter songs based on the selected emotion
    emotion_songs = song_data[song_data['emotion'] == emotion]
    # Randomly select up to 9 songs from the filtered list
    selected_songs = emotion_songs.sample(min(9, len(emotion_songs)))
    # Return a list of dictionaries containing song information
    return selected_songs[['artist_name', 'track_name', 'year']].to_dict(orient='records')

@app.route('/')
def index():
    return render_template('fe2_index.html')

@app.route('/play_selected_song', methods=['POST'])
def play_selected_song():
    selected_song = request.json['selected_song']
    play_song(selected_song)
    return jsonify({'status': 'success'})

@app.route('/recommend-songs-emotion', methods=['POST'])
def recommend_songs_emotion_route():
    selected_emotion = request.form['emotion']
    recommended_emotion = recommend_songs_emotion(selected_emotion)
    return render_template('emotion_recommendation.html', songs=recommended_emotion, emotion=selected_emotion)

if __name__ == '__main__':
    app.run(debug=True, port=5009)