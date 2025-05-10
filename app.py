import streamlit as st
import requests
import random
import os

# Load your Google Books API Key from environment variables (recommended)
GOOGLE_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")  # Use secrets on Streamlit Cloud

st.set_page_config(page_title="Book Vibe Matcher", layout="centered")

st.title("📚 Book Vibe Matcher")
st.write("Enter 3 books you love, and we’ll recommend a similar one.")

# Input form
with st.form("book_form"):
    book1 = st.text_input("Book #1", "The Stainless Steel Rat")
    book2 = st.text_input("Book #2", "Leonardo da Vinci")
    book3 = st.text_input("Book #3", "The 33 Strategies of War")
    submitted = st.form_submit_button("Find Me a Book")

def search_google_books(query):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": 5,
        "printType": "books",
        "projection": "lite",
        "key": GOOGLE_API_KEY
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

def recommend_book(book_titles):
    recommendations = []
    for title in book_titles:
        primary = search_google_books(f'intitle:{title}')
        fallback = search_google_books(title)
        results = primary + fallback
        for book in results:
            if "id" in book:
                recommendations.append(book)

    # Filter duplicates
    seen = set()
    unique_books = []
    for book in recommendations:
        if book["id"] not in seen:
            seen.add(book["id"])
            unique_books.append(book)

    return random.choice(unique_books) if unique_books else None

if submitted:
    with st.spinner("Searching for your next great read..."):
        titles = [book1, book2, book3]
        rec = recommend_book(titles)

        if rec:
            info = rec["volumeInfo"]
            st.subheader(info.get("title", "Untitled"))
            st.write(f"**Author(s):** {', '.join(info.get('authors', ['Unknown']))}")
            st.write(info.get("description", "No description available."))

            if "imageLinks" in info:
                st.image(info["imageLinks"].get("thumbnail"), width=160)

            if "infoLink" in info:
                st.markdown(f"[More about this book →]({info['infoLink']})")
        else:
            st.warning("Still no match! Try different titles or check your API key.")
