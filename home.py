import streamlit as st
import pickle
import requests


# import pages.other_page as other_page

st.set_page_config(
    page_title="projet2-movie-system-reco",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded",
)


# .........................................................................................................
# RECOMMENDATION SYSTEM
# .........................................................................................................

# Load the movie data, TF-IDF vectorizer, and KNN model from pickle files
movies = pickle.load(open("movies_list.pkl", "rb"))
tfidf_vectorizer = pickle.load(open("tfidf_vectorizer.pkl", "rb"))
knn_model = pickle.load(open("knn_model.pkl", "rb"))
movies_list = movies["movieTitle"].values

# Replace 'YOUR_API_KEY' with your actual API key
API_KEY = "14ba68fd10b28f2b824269c4a5c78960"


# Fetch movie details using movie ID from TMDb API
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits"
    response = requests.get(url)
    data = response.json()

    director_name = ""
    actor_names = []
    movie_link = ""

    if "credits" in data:
        directors = [
            crew["name"]
            for crew in data["credits"]["crew"]
            if crew["job"] == "Director"
        ]
        director_name = ", ".join(directors)
        actors = [actor["name"] for actor in data["credits"]["cast"]]
        actor_names = actors[:5]

    movie_link = data.get("homepage")

    return director_name, actor_names, movie_link


# Fetch movie poster using movie ID from TMDb API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "poster_path" in data and data["poster_path"]:
        base_url = "https://image.tmdb.org/t/p/"
        poster_size = "w500"
        poster_url = f"{base_url}{poster_size}{data['poster_path']}"
        return poster_url, fetch_movie_details(movie_id)
    else:
        return None, None


# Define the recommendation function
def recommend(movie, n_recommendations=10):
    try:
        movie_index = movies[movies["movieTitle"] == movie].index[0]
    except IndexError:
        st.error("Movie not found in the dataset.")
        return [], [], [], [], [], [], []

    movie_genres = movies.loc[movie_index, "genres"].split(",")
    movie_tag_tfidf = tfidf_vectorizer.transform([movies.loc[movie_index, "f_tags"]])

    distances, indices = knn_model.kneighbors(movie_tag_tfidf, n_neighbors=100)
    indices = indices.flatten()

    recommended_movies = []
    recommended_posters = []
    recommended_genres = []
    recommended_overviews = []
    recommended_actors = []
    recommended_directors = []
    recommended_links = []

    for idx in indices:
        if len(recommended_movies) >= n_recommendations:
            break

        recommended_movie_genres = movies.loc[idx, "genres"].split(",")
        if any(genre in movie_genres for genre in recommended_movie_genres):
            movie_title = movies.loc[idx, "movieTitle"]
            movie_id = movies.loc[idx, "titleId"]
            poster_url, movie_details = fetch_poster(movie_id)

            if poster_url and movie_details:
                recommended_movies.append(movie_title)
                recommended_posters.append(poster_url)
                recommended_genres.append(movies.loc[idx, "genres"])
                recommended_overviews.append(movies.loc[idx, "overview"])
                recommended_actors.append(", ".join(movie_details[1]))
                recommended_directors.append(movie_details[0])
                recommended_links.append(movie_details[2])

    return (
        recommended_movies,
        recommended_posters,
        recommended_genres,
        recommended_overviews,
        recommended_actors,
        recommended_directors,
        recommended_links,
    )


st.markdown(
    '<h1 style="text-align: center;">Movie Recommendation System</h1>',
    unsafe_allow_html=True,
)

selectValue = st.selectbox("Select your movie", movies_list)

# Default movie recommendations
num_default_rows = 1
num_default_cols = 20

st.markdown(
    '<h5 style="text-align: center;">YOUR MOVIES</h5>',
    unsafe_allow_html=True,
)

# start_idx = 2  # Start from the third movie
# num_default_rows = 1
# num_default_cols = 5

# for i in range(num_default_rows):
#     row = st.columns(num_default_cols)
#     for j in range(num_default_cols):
#         idx = start_idx + (i * num_default_cols + j)
#         if idx < len(movies_list):
#             movie_id = movies.loc[idx, "titleId"]
#             poster_url, movie_details = fetch_poster(movie_id)
#             if poster_url and movie_details:
#                 with row[j]:
#                     st.markdown(
#                         f"""
#                         <div style="background-color: DarkGoldenRod ; width: 220px; height: 310px; margin-left: 20px; margin-right: 20px; margin-bottom: 20px; display: flex; justify-content: center; align-items: center;">
#                              {'<img src="' + poster_url + '" style="width: 210px; height: 300px;" />' if poster_url else '<p>No poster available</p>'}
#                         </div>
#                         """,
#                         unsafe_allow_html=True,
#                     )

# st.markdown(
#     """
#       <hr>
#     """,
#     unsafe_allow_html=True,
# )

if st.button("Search for Recommendation"):
    (
        recommended_movies,
        recommended_posters,
        recommended_genres,
        recommended_overviews,
        recommended_actors,
        recommended_directors,
        recommended_links,
    ) = recommend(selectValue)

    num_rows = 10
    num_cols = 1
    for i in range(num_rows):
        row = st.columns(num_cols)
        for j in range(num_cols):
            idx = i * num_cols + j
            if idx < len(recommended_movies):
                with row[j]:
                    st.markdown(
                        f"""
                        <div style="background-color: tomato; border-radius: 1%; width: 100%; height: 340px; display: flex; align-items: center; margin-bottom: 10px;">
                            <div style="flex: 0 0 100px;">
                                {'<img src="' + recommended_posters[idx] + '" style="width: 200px; height: 300px; padding-left: 10px" />' if recommended_posters[idx] else '<p>No poster available</p>'}
                            </div>
                            <div style="flex: 1; padding-left: 20px; padding-right: 20px">
                                <div>
                                    <p style="margin: 0;"><strong style="color: white;">Title: </strong> {recommended_movies[idx]}</p>
                                    <p style="margin: 0;"><strong style="color: white;">Genres: </strong> {recommended_genres[idx]}</p>
                                    <p style="margin: 0;"><strong style="color: white;">Overview: </strong> {recommended_overviews[idx]}</p>
                                    <p style="margin: 0;"><strong style="color: white;">Director: </strong> {recommended_directors[idx]}</p>
                                    <p style="margin: 0;"><strong style="color: white;">Actors: </strong> {recommended_actors[idx]}</p>
                                </div>
                                <div style="margin-top: 15px;">
                                    <a type="button" href="{recommended_links[idx]}" style="background-color: green; color: white; padding: 10px 15px; text-decoration: none; border-radius: 50%; box-shadow: 1px 1px;"> Details </a>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
