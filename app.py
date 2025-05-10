import streamlit as st
import requests
import random

st.set_page_config(page_title="Book Vibe Matcher", layout="centered")

st.title("📚 Book Vibe Matcher")
st.write("Enter 3 books you love, and we’ll recommend a similar one.")

# Input form
with st.form("book_form"):
    book1 = st.text_input("Book #1")
    book2 = st.text_input("Book #2")
    book3 = st.text_input("Book #3")
    submitted = st.form_submit_button("Find Me a Book")

def search_google_books(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={requests.utils.quote(query)}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        if "items" in results:
            return results["items"]
    return []

def recommend_book(book_titles):
    recommendations = []
    for title in book_titles:
        books = search_google_books(title)
        if books:
            recommendations.extend(books)
    
    # Remove duplicates and shuffle
    seen = set()
    unique_recs = []
    for book in recommendations:
        book_id = book["id"]
        if book_id not in seen:
            seen.add(book_id)
            unique_recs.append(book)
    
    # Pick a random one
    if unique_recs:
        return random.choice(unique_recs)
    return None

if submitted:
    with st.spinner("Searching for your next great read..."):
        titles = [book1, book2, book3]
        recommended = recommend_book(titles)
        
        if recommended:
            info = recommended["volumeInfo"]
            st.subheader(info.get("title", "Unknown Title"))
            st.write(f"**Author(s):** {', '.join(info.get('authors', ['Unknown']))}")
            st.write(info.get("description", "No description available."))
            if "imageLinks" in info:
                st.image(info["imageLinks"].get("thumbnail", ""), width=150)
            if "infoLink" in info:
                st.markdown(f"[More info →]({info['infoLink']})")
        else:
            st.warning("Sorry, we couldn’t find a good recommendation.")
