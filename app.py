import streamlit as st
import requests
from urllib.parse import quote

# Last.fm API key
API_KEY = '60a80eb83b68b7487371c43ab7d232fa'

def get_similar_artists(artist):
    url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist={quote(artist)}&api_key={API_KEY}&format=json&limit=5"
    response = requests.get(url)
    data = response.json()

    if 'similarartists' not in data or 'artist' not in data['similarartists']:
        return []
    
    similar = []
    for a in data['similarartists']['artist']:
        match_score = round(float(a.get('match', 0)) * 100, 1)
        similar.append({
            'name': a['name'],
            'url': a['url'],
            'image': a['image'][-1]['#text'] if a['image'] else '',
            'match_score': match_score,
            'youtube_url': f"https://www.youtube.com/results?search_query={quote(a['name'])}"
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
st.set_page_config(page_title="🎶 Obscure Song Finder", layout="centered")
st.title("🎶 Obscure Song Finder (via Last.fm)")
st.write("Find lesser-known artists who match the vibe of your favorite.")

artist_input = st.text_input("🎤 Enter Artist Name")

if st.button("🔍 Find Similar Artists"):
    if not artist_input:
        st.error("Please enter an artist name.")
    else:
        with st.spinner("Searching for matches..."):
            matches = get_similar_artists(artist_input)
            artist_img, artist_bio = get_artist_info(artist_input)

        if matches:
            st.markdown(f"### 🔎 Artists similar to **{artist_input}**:")
            for m in matches:
                st.image(m['image'] or "https://via.placeholder.com/150", width=160)
                st.markdown(f"**{m['name']}**")
                st.markdown(f"[🔗 View on Last.fm]({m['url']})")
                st.markdown(f"[📺 YouTube Search]({m['youtube_url']})")
                st.slider("🎚️ Match Score", 0, 100, int(m['match_score']), disabled=True)
                st.markdown("---")
            
            st.subheader(f"🧠 About {artist_input}")
            if artist_img:
                st.image(artist_img, width=160)
            st.write(artist_bio)
        else:
            st.warning("No similar artists found. Try a different name.")

