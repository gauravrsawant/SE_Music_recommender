from flask import Flask, render_template, request, jsonify
import cv2
from deepface import DeepFace
import base64
import numpy as np
import csv
import requests
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
import time
app = Flask(__name__)

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function to detect emotion in an image
def detect_emotion(img_data):
    # Decode base64 image data
    img_bytes = base64.b64decode(img_data.split(',')[1])
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Convert grayscale frame to RGB format
    rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    emotions = []

    for (x, y, w, h) in faces:
        # Extract the face ROI (Region of Interest)
        face_roi = rgb_frame[y:y + h, x:x + w]
        
        # Perform emotion analysis on the face ROI
        result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
        
        # Determine the dominant emotion
        emotion = result[0]['dominant_emotion']
        emotions.append(emotion)

    return emotions

# Function to get random songs based on detected emotion
def get_random_songs(emotion):
    try:
        with open(f'songs/{emotion}.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            songs = list(reader)
        random.shuffle(songs)  # Shuffle the list of songs
        return songs[:5]  # Return first 5 random songs
    except FileNotFoundError:
        return []


# Define route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Define route for emotion detection
@app.route('/detect_emotion', methods=['POST'])
def detect_emotion_route():
    # Receive image data from frontend
    img_data = request.json['image_data']
    
    # Detect emotion in the image
    emotions = detect_emotion(img_data)

    if emotions:
        # Get most frequent emotion
        emotion = max(set(emotions), key=emotions.count)
        # Get songs based on detected emotion
        songs = get_random_songs(emotion)
        if songs:
            # Generate HTML table for songs
            songs_html = '<table>'
            songs_html += '<tr><th>Title</th><th>Album</th><th>Artist</th></tr>'
            for song in songs:
                songs_html += f'<tr><td>{song[0]}</td><td>{song[1]}</td><td>{song[2]}</td></tr>'
            songs_html += '</table>'
            # Return data as JSON
            return jsonify(emotion=emotion, songsHtml=songs_html)
        else:
            return jsonify(emotion='No songs found', songsHtml='')
    else:
        return jsonify(emotion='No face detected', songsHtml='')
import requests
import webbrowser
import spotipy

client_id = 'f17085dc406f4736811fb37b3990077c'
client_secret = '15b9da1fa07e4fc19d7289ceac8e1b39'

SPOTIFY_TOKEN = "https://accounts.spotify.com/api/token"
request_body = {
    "grant_type": "client_credentials",
    "code": "code",
    "redirect_uri": 'http://localhost:8888/callback',
    "client_id": client_id,
    "client_secret": client_secret,
}
r = requests.post(url=SPOTIFY_TOKEN, data=request_body)
resp = r.json()['access_token']
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
client = spotipy.Spotify(auth=resp)

def play_song(track_name):
    results = spotify.search(q='track:%s' % track_name, type='track')
    if results['tracks']['total'] == 0:
        print("Song not found. Please try again.")
    else:
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        webbrowser.open(track_uri)
        
def play_song(track_name):
    results = spotify.search(q='track:%s' % track_name, type='track')
    if results['tracks']['total'] == 0:
        print("Song not found. Please try again.")
    else:
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        # Open the track URI in the default web browser
        webbrowser.open(track_uri)
        # Wait for a brief moment to ensure the web browser is opened
        time.sleep(1)
        # Use Spotipy to play the track (if Spotipy is properly set up)
        client.start_playback(uris=[track_uri])
        
# Define route to play the selected song
@app.route('/play_selected_song', methods=['POST'])
def play_selected_song():
    selected_song = request.json['selected_song']
    play_song(selected_song)

if __name__ == '__main__':
    app.run(debug=True)
