import streamlit as st
import requests
import base64

# -----------------------
# CONFIGURATION
# -----------------------
CLIENT_ID = "2fd09035ff5548a09b2fb8150648a824"
CLIENT_SECRET = "8450f8417aff4816bef7c3c8cd129fa4"

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

    r = requests.post(auth_url, headers=headers, data=data)
    token = r.json().get("access_token")
    return token

# -----------------------
# SEARCH FOR INPUT SONG
# -----------------------
def search_track(song, artist, token):
    query = f"track:{song} artist:{artist}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    r = requests.get(url, headers=headers)
    items = r.json().get("tracks", {}).get("items")
    if items:
        return items[0]
    else:
        return None

# -----------------------
# GET RECOMMENDATIONS
# -----------------------
def get_recommendations(seed_track_id, token):
    url = f"https://api.spotify.com/v1/recommendations?seed_tracks={seed_track_id}&limit=5&min_popularity=10&max_popularity=40"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    r = requests.get(url, headers=headers)
    return r.json().get("tracks", [])

# -----------------------
# STREAMLIT APP
# -----------------------
st.title("🎧 Obscure Song Finder")
st.subheader("Find obscure tracks that sound like your favorite song.")

song = st.text_input("Enter song title:")
artist = st.text_input("Enter artist name:")

if st.button("Find Obscure Songs"):
    if song and artist:
        with st.spinner("Contacting Spotify..."):
            token = get_spotify_token()
            original_track = search_track(song, artist, token)

            if original_track:
                st.success(f"Found: {original_track['name']} by {original_track['artists'][0]['name']}")

                recommendations = get_recommendations(original_track['id'], token)
                st.write("### 🎶 You might like:")

                for rec in recommendations:
                    rec_name = rec['name']
                    rec_artist = rec['artists'][0]['name']
                    link = rec['external_urls']['spotify']
                    img = rec['album']['images'][0]['url'] if rec['album']['images'] else None

                    if img:
                        st.image(img, width=200)
                    st.markdown(f"**{rec_name}** by *{rec_artist}*")
                    st.markdown(f"[▶️ Listen on Spotify]({link})")
                    st.markdown("---")
            else:
                st.error("Could not find that track. Check your spelling.")
    else:
        st.warning("Please enter both song and artist name.")
