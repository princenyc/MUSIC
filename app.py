import streamlit as st
import requests
import os

# -----------------------
# Last.fm API setup
# -----------------------
API_KEY = os.getenv("LASTFM_API_KEY")  # Put this in Streamlit secrets

# -----------------------
# Get similar tracks from Last.fm
# -----------------------
def get_similar_tracks(artist, track):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.getsimilar",
        "artist": artist,
        "track": track,
        "api_key": API_KEY,
        "format": "json",
        "limit": 10
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        return res.json().get("similartracks", {}).get("track", [])
    except Exception as e:
        return f"❌ Error: {e}"

# -----------------------
# Streamlit App UI
# -----------------------
st.title("🎧 Obscure Song Finder (Last.fm Edition)")
st.subheader("Discover lesser-known songs similar to your favorites.")

song = st.text_input("Enter song title:")
artist = st.text_input("Enter artist name:")

if st.button("Find Obscure Songs"):
    if song and artist:
        with st.spinner("🔍 Searching Last.fm..."):
            results = get_similar_tracks(artist, song)

        if isinstance(results, str):
            st.error(results)
        elif not results:
            st.warning("😕 No similar obscure songs found.")
        else:
            st.markdown("### 🎵 Recommendations")
            for track in results:
                title = track["name"]
                artist_name = track["artist"]["name"]
                url = f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}+{artist_name.replace(' ', '+')}"
                match_score = round(float(track.get("match", 0)) * 100)

                st.markdown(f"**{title}** by *{artist_name}* — Match score: {match_score}%")
                st.markdown(f"[▶️ Search on YouTube]({url})")
                st.markdown("---")
    else:
        st.info("👈 Please enter both a song and artist to begin.")
