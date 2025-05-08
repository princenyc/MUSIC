import streamlit as st
import requests
from urllib.parse import quote

# Replace with your Last.fm API key
API_KEY = 'your_lastfm_api_key'

def get_similar_tracks(artist, track):
    url = f"http://ws.audioscrobbler.com/2.0/?method=track.getsimilar&artist={quote(artist)}&track={quote(track)}&api_key={API_KEY}&format=json&limit=5"
    response = requests.get(url)
    data = response.json()
    
    if 'similartracks' not in data or 'track' not in data['similartracks']:
        return []
    
    similar = []
    for t in data['similartracks']['track']:
        match_score = round(float(t.get('match', 0)) * 100, 1)  # Last.fm gives 0–1 match
        similar.append({
            'name': t['name'],
            'artist': t['artist']['name'],
            'url': t['url'],
            'image': t['image'][-1]['#text'] if t['image'] else '',
            'match_score': match_score,
            'youtube': f"https://www.youtube.com/results?search_query={quote(t['name'] + ' ' + t['artist']['name'])}"
        })
    return similar

def get_artist_bio(artist):
    url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={quote(artist)}&api_key={API_KEY}&format=json"
    response = requests.get(url)
    data = response.json()
    if 'artist' in data and 'bio' in data['artist']:
        return data['artist']['bio']['summary']
    return "No bio available."

# Streamlit UI
st.title("🎧 Obscure Song Recommender (Last.fm)")
st.write("Find songs that sound like your favorite but aren't on everyone's playlist.")

artist_input = st.text_input("Enter Artist Name")
song_input = st.text_input("Enter Song Name")

if st.button("🔍 Find Obscure Songs"):
    if artist_input and song_input:
        similar_tracks = get_similar_tracks(artist_input, song_input)

        if similar_tracks:
            st.success(f"Found similar songs to **{song_input}** by **{artist_input}**:")
            for track in similar_tracks:
                st.image(track['image'] or "https://via.placeholder.com/150", width=150)
                st.markdown(f"**{track['name']}** by *{track['artist']}*")
                st.markdown(f"[🎵 Listen on Last.fm]({track['url']})")
                st.markdown(f"[📺 YouTube Search]({track['youtube']})")
                st.slider("Match Score", 0, 100, int(track['match_score']), disabled=True)
                st.markdown("—")
            
            st.subheader("🎤 About the Artist")
            bio = get_artist_bio(artist_input)
            st.write(bio)
        else:
            st.warning("No similar songs found. Try another track.")
    else:
        st.error("Please enter both artist and song.")


