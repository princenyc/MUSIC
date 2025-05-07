import streamlit as st
import requests
import os

# -----------------------
# API Config
# -----------------------
API_KEY = os.getenv("LASTFM_API_KEY")

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
        return []

# -----------------------
# Get artist info (bio + image)
# -----------------------
def get_artist_info(artist_name):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "artist.getinfo",
        "artist": artist_name,
        "api_key": API_KEY,
        "format": "json"
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json().get("artist", {})
        summary = data.get("bio", {}).get("summary", "No bio available.")
        image = next((img["#text"] for img in data.get("image", []) if img["size"] == "extralarge"), "")
        return summary.split("<a")[0].strip(), image
    except:
        return "No bio available.", ""

# -----------------------
# Streamlit App
# -----------------------
st.title("🎧 Obscure Song Finder (Last.fm Edition)")
st.subheader("Find lesser-known songs similar to your favorites.")

st.markdown("**ℹ️ Match Score** reflects how closely a recommended track resembles the original song, based on Last.fm's listener data.")

song = st.text_input("Enter song title:")
artist = st.text_input("Enter artist name:")
min_score = st.slider("Minimum Match Score", 0, 100, 60)

if st.button("Find Obscure Songs"):
    if song and artist:
        with st.spinner("🔍 Searching..."):
            results = get_similar_tracks(artist, song)

        if not results:
            st.warning("😕 No similar obscure songs found.")
        else:
            filtered = [track for track in results if float(track.get("match", 0)) * 100 >= min_score]

            if not filtered:
                st.info(f"No tracks found with match score ≥ {min_score}%. Try lowering the threshold.")
            else:
                st.markdown("### 🔎 Recommendations")
                for track in filtered:
                    title = track["name"]
                    artist_name = track["artist"]["name"]
                    score = round(float(track["match"]) * 100)
                    yt_link = f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}+{artist_name.replace(' ', '+')}"

                    bio, image_url = get_artist_info(artist_name)

                    st.markdown(f"**{title}** by *{artist_name}* — Match Score: `{score}%`")
                    st.markdown(f"[▶️ Search on YouTube]({yt_link})")
                    if image_url:
                        st.image(image_url, width=150)
                    st.markdown(f"📘 *{bio}*")
                    st.markdown("---")
    else:
        st.info("👈 Please enter both a song and artist to begin.")

