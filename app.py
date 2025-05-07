import streamlit as st
import requests
import base64

# -----------------------
# CONFIGURATION
# -----------------------
CLIENT_ID = "2fd09035ff5548a09b2fb8150648a824"        # 👈 Replace this
CLIENT_SECRET = "8450f8417aff4816bef7c3c8cd129fa4"  # 👈 Replace this

# -----------------------
# AUTHENTICATE WITH SPOTIFY
# -----------------------
def get_spotify_token():
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}"
    }
    data = {
        "grant_type": "client_credentials"
    }

    try:
        r = requests.post(auth_url, headers=headers, data=data)
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception as e:
        st.error("❌ Failed to get Spotify token. Check your Client ID and Secret.")
        st.stop()

# -----------------------
# SEARCH FOR INPUT SONG
# -----------------------
def search_track(song, artist, token):
    query = f"track:{song} artist:{artist}"
    url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": query,
        "type": "track",
        "limit": 1
    }

    try:
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        items = r.json().get("tracks", {}).get("items")
        return items[0] if items else None
    except Exception:
        return None

# -----------------------
# GET RECOMMENDATIONS
# -----------------------
def get_recommendations(seed_track_id, token):
    url = "https://api.spotify.com/v1/recommendations"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "seed_tracks": seed_track_id,
        "limit": 5,
        "min_popularity": 10,
        "max_popularity": 40
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("tracks", [])
    except Exception as e:
        return []

# -----------------------
# STREAMLIT APP
# -----------------------
st.title("🎧 Obscure Song Finder")
st.subheader("Find obscure Spotify songs that sound like your favorite track.")

song = st.text_input("Enter song title:")
artist = st.text_input("Enter artist name:")

if st.button("Find Obscure Songs"):
    if song and artist:
        with st.spinner("🎵 Searching Spotify..."):
            token = get_spotify_token()
            track = search_track(song, artist, token)

            if not track:
                st.error("⚠️ Could not find that track. Double-check the spelling and try again.")
                st.stop()

            st.success(f"Found: {track['name']} by {track['artists'][0]['name']}")

            try:
                recommendations = get_recommendations(track['id'], token)
            except Exception as e:
                st.error("Something went wrong while getting recommendations. Try another song or check your network.")
                st.stop()

            if not recommendations:
                st.warning("😕 Spotify couldn't find similar obscure songs for that track. Try a different one.")
            else:
                st.write("### 🔍 You might like:")
                for rec in recommendations:
                    name = rec['name']
                    artist_name = rec['artists'][0]['name']
                    link = rec['external_urls']['spotify']
                    img = rec['album']['images'][0]['url'] if rec['album']['images'] else None

                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if img:
                            st.image(img, width=100)
                    with col2:
                        st.markdown(f"**{name}** by *{artist_name}*")
                        st.markdown(f"[▶️ Listen on Spotify]({link})")
                    st.markdown("---")
    else:
        st.info("👈 Please enter both a song title and an artist name to begin.")

