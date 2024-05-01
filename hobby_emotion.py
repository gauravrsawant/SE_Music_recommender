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
