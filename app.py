import streamlit as st
import requests
from urllib.parse import quote

API_KEY = 'your_lastfm_api_key'

def get_similar_tracks(artist, song, limit=5):
    url = f"http://ws.audioscrobbler.com/2.0/?method=track.getsimilar&artist={quote(artist)}&track={quote(song)}&api_key={API_KEY}&format=json&limit={limit}"
    response = requests.get(url)
    data = response.json()

    results = []
    if 'similartracks' in data and 'track' in data['similartracks']:
        for t in data['similartracks']['track']:
            match_score = round(float(t.get('match', 0)) * 100, 1)
            results.append({
                'track_name': t['name'],
                'artist_name': t['artist']['name'],
                'match_score': match_score,
                'lastfm_url': t['url'],
                'youtube_url': f"https://www.youtube.com/results?search_query={quote(t['name'] + ' ' + t['artist']['name'])}"
            })
    return results

def get_artist_info(artist):
    url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={quote(artist)}&api_key={API_KEY}&format=json"
    response = requests.get(url)
    data = response.json()
    if 'artist' in data:
        image = data['artist']['image'][-1]['#text'] if data['artist']['image'] else ''
        bio = data['artist']['bio']['summary'].split('<a')[0].strip()
        return image, bio
    return '', 'No bio available.'

# ——— Streamlit UI ——— #
st.set_page_config(page_title="🎶 Obscure Song Finder", layout="centered")
st.title("🎶 Obscure Song Finder")
st.write("Enter an artist and a song to find obscure tracks that match the vibe.")
