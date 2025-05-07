import streamlit as st
import requests
import base64

# -----------------------
# CONFIGURATION
# -----------------------
CLIENT_ID = "your_spotify_client_id"        # 👈 Replace this
CLIENT_SECRET = "your_spotify_client_secret"  # 👈 Replace this

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
        if not items:
            return None
        track = items[0]
        return {
            "track_id": track["id"],
            "artist_id": track["artists"][0]["id"],
            "track_name": track["name"],
            "artist_name": track["artists"][0]["name"],
            "album_image": track["album"]["images"][0]["url"] if track["album"]["images"] else None
        }
    except Exception:
        return None

# -----------------------
# GET GENRES FOR ARTIST
# -----------------------
def get_artist_genres(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json().get("genres", [])
    except Exception:
        return []

# -----------------------
# GET SMART RECOMMENDATIONS
# -----------------------
def get_recommendations(seed_track_id, seed_artist_id, token):
    base_url = "https://api.spotify.com/v1/recommendations"
    headers = {"Authorization": f"Bearer {token}"}

    genres = get_artist_genres(seed_artist_id, token)
    genre_seed = genres[0] if genres else None

    # First try: track + artist + genre
    params = {
        "limit": 5,
        "min_popularity": 5,
        "max_popularity": 65,
        "seed_tracks": seed_track_id,
        "seed_artists": seed_artist_id
    }
    if genre_seed:
        params["seed_genres"] = genre_seed

    r = requests.get(base_url, headers=headers, params=params)
    if r.status_code == 200 and r.json().get("tracks"):
        return r.json().get("tracks")

    # Fallback: artist + genre
    if genre_seed:
        fallback_params = {
            "limit": 5,
            "min_popularity": 5,
            "max_popularity": 70,
            "seed_artists": seed_artist_id,
            "seed_genres": genre_seed
        }
        r2 = requests.get(base_url, headers=headers, params=fallback_params)
        if r2.status_code == 200 and r2.json().get("tracks"):
            return r2.json().get("tracks")

    # Final fallback: artist only
    fallback_params = {
        "limit": 5,
        "min_popularity": 5,
        "max_popularity": 70,
        "seed_artists": seed_artist_id
    }
    r3 = requests.get(base_url, headers=headers, params=fallback_params)
    if r3.status_code == 200:
        return r3.json().get("tracks", [])

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

            st.success(f"Found: {track['track_name']} by {track['artist_name']}")

            try:
                recommendations = get_recommendations(track["track_id"], track["artist_id"], token)
            except Exception as e:
                st.error("Something went wrong while getting recommendations.")
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
