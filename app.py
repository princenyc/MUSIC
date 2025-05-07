import streamlit as st
import requests
import base64

# -----------------------
# CONFIGURATION
# -----------------------
CLIENT_ID = "2fd09035ff5548a09b2fb8150648a824"  # ← REPLACE THIS
CLIENT_SECRET = "8450f8417aff4816bef7c3c8cd129fa4"  # ← REPLACE THIS

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
    url = f"https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": query,
        "type": "track",
        "limit": 1
    }

    r = requests.get(url, headers=headers, params=params)
    items = r.json().get("tracks", {}).get("items")
    return items[0] if items else None

# -----------------------
# GET RECOMMENDATIONS
# ---recommendations = get_recommendations(track['id'], token)

if not recommendations:
    st.warning("😕 Spotify couldn't find similar obscure songs for that track. Try a different one or check spelling.")
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


# -----------------------
# STREAMLIT APP
# -----------------------
st.title("🎧 Obscure Song Finder")
st.subheader("Find obscure Spotify tracks that sound like your favorite song.")

song = st.text_input("Enter song title:")
artist = st.text_input("Enter artist name:")

if st.button("Find Obscure Songs"):
    if song and artist:
        with st.spinner("🎵 Searching Spotify..."):
            token = get_spotify_token()
            track = search_track(song, artist, token)

            if track:
                st.success(f"Found: {track['name']} by {track['artists'][0]['name']}")
                recommendations = get_recommendations(track['id'], token)

                st.write("### 🔍 You might like:")
                for rec in recommendations:
                    name = rec['name']
                    artist_name = rec['artists'][0]['name']
                    link = rec['external_urls']['spotify']
                    img = rec['album']['images'][0]['url'] if rec['album']['images'] else None

                    if img:
                        st.image(img, width=200)
                    st.markdown(f"**{name}** by *{artist_name}*")
                    st.markdown(f"[▶️ Listen on Spotify]({link})")
                    st.markdown("---")
            else:
                st.error("⚠️ Couldn’t find that track. Double-check the spelling.")
    else:
        st.warning("Please enter both song title and artist name.")
