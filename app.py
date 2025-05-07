import streamlit as st
import openai

# -----------------------
# CONFIGURATION
# -----------------------
from openai import OpenAI

client = OpenAI(api_key="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")  # 👈 Replace key

def get_song_recommendations(song, artist):
    prompt = f"""
    I love the song "{song}" by {artist}. 
    Please recommend 2–3 obscure or underrated songs from lesser-known artists that sound similar in style, mood, and energy.
    For each, include:
    - Song title
    - Artist name
    - A 1-sentence reason it’s a good match
    - A Spotify or YouTube search link

    Keep the list concise and markdown formatted.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a music recommendation engine who loves obscure tracks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"


# -----------------------
# STREAMLIT APP
# -----------------------
st.title("🎧 Obscure Song Finder (OpenAI-Powered)")
st.subheader("Enter a song and artist to discover similar obscure tracks.")

song = st.text_input("Enter song title:")
artist = st.text_input("Enter artist name:")

if st.button("Find Obscure Songs"):
    if song and artist:
        with st.spinner("🧠 Thinking like a record store nerd..."):
            result = get_song_recommendations(song, artist)
        st.markdown("### 🎵 Recommendations")
        st.markdown(result)
    else:
        st.warning("Please enter both a song title and artist name.")

