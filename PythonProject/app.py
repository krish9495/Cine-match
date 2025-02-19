import pickle
import streamlit as st
import requests
import pandas as pd
import os

# Function to fetch movie poster from TMDB API
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=bce6210ae95b08f149c887961445d75c&language=en-US"
        response = requests.get(url)
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image+Available"  # Placeholder if no image
    except Exception as e:
        st.error(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=Error+Fetching+Image"

# Function to recommend similar movies
def recommend(movie):
    movie = movie.lower()  # Convert to lowercase for case-insensitive matching
    matching_movies = movies[movies['title'].str.lower() == movie]

    if matching_movies.empty:
        st.error("Selected movie not found in the database. Try another movie.")
        return [], []

    index = matching_movies.index[0]  # Get the index of the selected movie

    # Sort movies based on similarity score
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:  # Get top 5 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movie_names, recommended_movie_posters


# Streamlit App Title
st.header('🎬 Movie Recommender System')

# Load Movie Data
if not os.path.exists('movie_dict.pkl') or not os.path.exists('similarity.pkl'):
    st.error("Missing model files! Ensure 'movie_dict.pkl' and 'similarity.pkl' exist in the 'model' folder.")
else:
    # Load movie dictionary and convert to DataFrame
    movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movie_dict)  # Convert dictionary to DataFrame
    similarity = pickle.load(open('similarity.pkl', 'rb'))

    # Debugging Prints (can remove later)
    print(type(movies), type(similarity))
    print(movies.head())  # Now this should work without error

    # Ensure 'movies' is a DataFrame
    if not isinstance(movies, pd.DataFrame) or 'title' not in movies.columns or 'movie_id' not in movies.columns:
        st.error("Error: 'movie_dict.pkl' is not in the expected format. Check your file.")
    elif len(similarity) != len(movies):
        st.error("Error: 'similarity.pkl' shape does not match the number of movies in 'movie_dict.pkl'. Check your file.")
    else:
        # Movie selection dropdown
        movie_list = movies['title'].values
        selected_movie = st.selectbox("🎥 Type or select a movie", movie_list)

        # Show recommendations when button is clicked
        if st.button('🔍 Show Recommendations'):
            recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

            if recommended_movie_names:
                cols = st.columns(5)  # Create 5 columns
                for col, name, poster in zip(cols, recommended_movie_names, recommended_movie_posters):
                    with col:
                        st.text(name)
                        st.image(poster)
