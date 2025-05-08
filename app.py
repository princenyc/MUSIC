import streamlit as st
import requests
from urllib.parse import quote

# Your Last.fm API key
API_KEY = 'your_lastfm_api_key'

# ——— Functions ——— #
def get_similar_tracks(artist, track):
    url = f"http://ws.audioscrobbler.com/2.0/?method=track.getsimilar&artist={quote(artist)}&track={quote(track)}&api_key={API_KEY}&format=json&limit=5"
    response = requests.get(url)
    data = response.json()

    if 'similartracks' not in data or 'track' not in data['similartracks']:
        return []
    
    similar = []
    for t in data['similartracks']['track']:
        match_score = round(float(t.get('match', 0)) * 100, 1)
        similar.append({
            'track_name': t['name'],
            'artist_name': t['artist']['name'],
            'url': t['url'],
            'image': t['image'][-1]['#text'] if t['image'] else '',
            'match_score': match_score,
            'youtube_url': f"https://www.youtube.com/results?search_query={quote(t['name'] + ' ' + t['artist']['name'])}"
        })
    return similar

def get_artist_info(artist):
    url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={quote(artist)}&api_key={API_KEY}&format=json"
    response = requests.get(url)
    data = response.json()
    if 'artist' in data:
        img = data['artist']['image'][-1]['#text'] if data['artist']['image'] else ''
        bio = data['artist']['bio']['summary']
        return img, bio
    return '', 'No bio available.'

# ——— Streamlit UI ——— #
st.set_page_config(page_title="Obscure Song Finder", page_icon="🎶")
st.title("🎶 Obscure Song Finder (via Last.fm)")
st.write("Find hidden tracks that match the vibe of your favorite song.")

artist_input = st.text_input("🎤 Enter Artist Name")
song_input = st.text_input("🎵 Enter Song Title")

if st.button("🔍 Find Matches"):
    if not artist_input or not song_input:
        st.error("Please enter both an artist and a song.")
    else:
        with st.spinner("Searching for hidden gems..."):
            matches = get_similar_tracks(artist_input, song_input)
            artist_img, artist_bio = get_artist_info(artist_input)

        if matches:
            st.markdown(f"### 🎯 Songs similar to *{song_input}* by *{artist_input}*")
            for m in matches:
                st.image(m['image'] or "https://via.placeholder.com/150", width=160)
                st.markdown(f"**🎵 {m['track_name']}** by **{m['artist_name']}**")
                st.markdown(f"[🔗 Listen on Last.fm]({m['url']})")
                st.markdown(f"[📺 YouTube Search]({m['youtube_url']})")
                st.slider("🎚️ Match Score", 0, 100, int(m['match_score']), disabled=True)
                st.markdown("---")
            
            st.subheader(f"🧠 About {artist_input}")
            if artist_img:
                st.image(artist_img, width=160)
            st.write(artist_bio)
        else:
            st.warning("Sorry — no similar songs found. Try a different track.")

