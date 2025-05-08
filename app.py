import streamlit as st
import requests
from urllib.parse import quote

API_KEY = 'your_lastfm_api_key'

def get_similar_artists(artist):
    url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist={quote(artist)}&api_key={API_KEY}&format=json&limit=5"
    response = requests.get(url)
    data = response.json()

    similar = []
    if 'similarartists' in data and 'artist' in data['similarartists']:
        for a in data['similarartists']['artist']:
            similar.append({
                'name': a['name'],
                'match_score': round(float(a.get('match', 0)) * 100, 1)
            })
    return similar

def get_artist_info(artist):
    url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={quote(artist)}&api_key={API_KEY}&format=json"
    response = requests.get(url)
    data = response.json()
    if 'artist' in data:
        image = data['artist']['image'][-1]['#text'] if data['artist']['image'] else ''
        bio = data['artist']['bio']['summary'].split('<a')[0].strip()
        return image, bio
    return '', 'No bio available.'

def get_top_tracks(artist, max_tracks=1):
    url = f"http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks&artist={quote(artist)}&api_key={API_KEY}&format=json&limit={max_tracks}"
    response = requests.get(url)
    data = response.json()
    
    tracks = []
    if 'toptracks' in data and 'track' in data['toptracks']:
        for t in data['toptracks']['track']:
            title = t['name']
            tracks.append({
                'title': title,
                'youtube_url': f"https://www.youtube.com/results?search_query={quote(title + ' ' + artist)}"
            })
    return tracks

# ——— Streamlit UI ——— #
st.set_page_config(page_title="🎶 Obscure Music Recommender", layout="centered")
st.title("🎶 Obscure Music Recommender (via Last.fm)")
st.write("Enter an artist to discover similar artists, their songs, trivia, and vibes.")

artist_input = st.text_input("🎤 Enter Artist Name")

if st.button("🔍 Find Obscure Songs"):
    if not artist_input:
        st.error("Please enter an artist name.")
    else:
        with st.spinner("Finding deep cuts and fun facts..."):
            similar_artists = get_similar_artists(artist_input)
            original_image, original_bio = get_artist_info(artist_input)

        if similar_artists:
            st.markdown(f"## 🔎 Artists similar to **{artist_input}**")

            for artist in similar_artists:
                image, trivia = get_artist_info(artist['name'])
                top_tracks = get_top_tracks(artist['name'], max_tracks=2)

                # Artist Header
                st.image(image or "https://via.placeholder.com/150", width=160)
                st.markdown(f"### 🎤 {artist['name']}")
                st.slider("🎚️ Match Score", 0, 100, int(artist['match_score']), disabled=True)
                st.caption(f"🧠 Trivia: {trivia[:250]}...")  # 1-line trivia

                for t in top_tracks:
                    st.markdown(f"🎵 **{t['title']}** — [📺 YouTube Search]({t['youtube_url']})")

                st.markdown("---")

            st.subheader(f"🧠 About {artist_input}")
            if original_image:
                st.image(original_image, width=160)
            st.write(original_bio)
        else:
            st.warning("No similar artists found. Try another name.")

