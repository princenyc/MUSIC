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
    except Exception:
        st.error("❌ Failed to get Spotify token. Check your Client ID and Secret.")
        st.stop()

# -----------------------
# SEARCH FOR INPUT SONG
# -----------------------
def search_track(song, artist, token):
    query = f"track:{song} artist:{artist}"
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": 1}

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
# GET SMART RECOMMENDATIONS WITH FALLBACK
# -----------------------
def get_recommendations(seed_artist_id, genre_seed, token, min_popularity, max_popularity):
    base_url = "https://api.spotify.com/v1/recommendations"
    headers = {"Authorization": f"Bearer {token}"}

    # Primary: artist + genre
    params = {
        "limit": 5,
        "min_popularity": min_popularity,
        "max_popularity": max_popularity,
        "seed_artists": seed_artist_id
    }
    if genre_seed:
        params["seed_genres"] = genre_seed

    r = requests.get(base_url, headers=headers, params=params)
    if r.status_code == 200 and r.json().get("tracks"):
        return r.json().get("tracks")

    # Fallback: artist only
    fallback_params = {
        "limit": 5,
        "seed_artists": seed_artist_id,
        "min_popularity": min_popularity,
        "max_popularity": max_popularity
    }
    r2 = requests.get(base_url, headers=headers, params=fallback_params)
    if r2.status_code == 200:
        return r2.json().get("tracks", [])

    return []

# -----------------------
# STREAMLIT APP
# -----------------------
st.title("🎧 Obscure Song Finder")
st.subheader("Find obscure Spotify songs that sound like your favorite track.")

song = st.text_input("Enter song title:")
artist = st.text_input("Enter artist name:")

with st.expander("🎚️ Customize Search"):
    min_pop = st.slider("Minimum Popularity", 0, 100, 5)
    max_pop = st.slider("Maximum Popularity", 0, 100, 70)

if st.button("Find Obscure Songs"):
    if song and artist:
        with st.spinner("🎵 Searching Spotify..."):
            token = get_spotify_token()
            track = search_track(song, artist, token)

            if not track:
                st.error("⚠️ Could not find that track. Double-check the spelling and try again.")
                st.stop()

            st.success(f"Found: {track['track_name']} by {track['artist_name']}")
            genre_seed = None
            try:
                genres = get_artist_genres(track["artist_id"], token)
                if genres:
                    genre_seed = genres[0]
            except:
                pass

            try:
                recommendations = get_recommendations(track["artist_id"], genre_seed, token, min_pop, max_pop)
            except Exception:
                st.error("Something went wrong while getting recommendations.")
                st.stop()

            if not recommendations:
                st.warning("😕 Spotify couldn't find similar obscure songs for that track. Try adjusting popularity range.")
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

