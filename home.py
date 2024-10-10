import streamlit as st
import pickle
import requests
import random

st.set_page_config(
    page_title="projet2-movie-system-reco",
    page_icon="🎬",
    layout="wide",
    # initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* Gradient for the Streamlit navbar with three colors and background opacity */
    header[data-testid="stHeader"] {
        background: linear-gradient(45deg, rgba(28, 28, 40, 0), rgba(75, 0, 130, 0) 40%, rgba(255, 165, 0, 0.5) 80%);
        backdrop-filter: blur(10px);  /* Optional: Adds a blur effect */
        color: white;
    }

    /* Ensure the navbar text remains fully visible and unaffected by opacity */
    header[data-testid="stHeader"] * {
        color: white;
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# # Inject custom CSS for navbar
# st.markdown(
#     """
#     <style>
#     /* Target the Streamlit navbar */
#     header[data-testid="stHeader"] {
#         background-color: transparent;
#         background-image: linear-gradient(45deg, rgba(255, 90, 205, 0.8), rgba(251, 218, 97, 0.8));
#         height: 70px;
#     }

#     /* Customize the text color inside the navbar */
#     header[data-testid="stHeader"] * {
#         color: white;
#     }

#     /* Remove the background shadow from the navbar */
#     header[data-testid="stHeader"]::before {
#         content: "";
#         display: block;
#         background-color: rgba(0, 0, 0, 0); /* Adjust opacity if needed */
#         height: 100%;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# Function to inject background CSS
def inject_background_css():
    background_css = """
        <style>
        /* Main container background with opacity overlay */
        [data-testid="stAppViewContainer"] {
            background-image: url("https://i.imgur.com/fmbehef.jpeg");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: scroll;
            position: fixed;
            z-index: 1;
        }

        /* Add a semi-transparent overlay on top of the background image */
        [data-testid="stAppViewContainer"]::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7); /* Adjust the opacity with this rgba value */
            z-index: 0;
        }
        </style>
    """

    # Apply the CSS styles
    st.markdown(background_css, unsafe_allow_html=True)


# Call the function to inject CSS
inject_background_css()

# Load the movie data, TF-IDF vectorizer, and KNN model from pickle files
movies = pickle.load(open("movies_list.pkl", "rb"))
tfidf_vectorizer = pickle.load(open("tfidf_vectorizer.pkl", "rb"))
knn_model = pickle.load(open("knn_model.pkl", "rb"))
movies_list = movies["movieTitle"].values

# Replace 'YOUR_API_KEY' with your actual API key
API_KEY = "14ba68fd10b28f2b824269c4a5c78960"


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

    # Fetch homepage or IMDb link
    movie_link = data.get("homepage")
    if not movie_link and "imdb_id" in data:
        imdb_id = data["imdb_id"]
        movie_link = f"https://www.imdb.com/title/{imdb_id}/"
    elif not movie_link:
        movie_link = "No official link available."

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


# Check if random movies have already been selected and stored in session state
if "random_movies" not in st.session_state:
    st.session_state["random_movies"] = random.sample(
        list(zip(movies_list, movies["titleId"].values)), 7
    )

# Display random movies above the title
row = st.columns(7)
for idx, (movie, movie_id) in enumerate(st.session_state["random_movies"]):
    poster_url, _ = fetch_poster(movie_id)  # Fetch the poster for each movie
    if poster_url:
        with row[idx]:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; height: 300px; margin-top: -50px; margin-left: -50px; margin-right: -50px;">
                    <img src="{poster_url}" style="width: auto; height: auto;" alt="{movie}" />
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        with row[idx]:  # If no poster is available, show a placeholder message
            st.markdown(
                """
                <div style="display: flex; justify-content: center;">
                    <p style="color: red;">Poster not available</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# Custom CSS for centering the selectbox
st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        margin-left: auto;
        margin-right: auto;
        display: block;
        width: 1000px;  /* Adjust the width as needed */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

selectValue = st.selectbox(
    "",
    options=["Select your movie for recommendation"] + list(movies_list),
    key="movie_selectbox",
)

# If a movie is selected, trigger the recommendation system
if selectValue and selectValue != "Select your movie for recommendation":
    (
        recommended_movies,
        recommended_posters,
        recommended_genres,
        recommended_overviews,
        recommended_actors,
        recommended_directors,
        recommended_links,
    ) = recommend(selectValue)

    # Display recommended movies
    num_rows = 10
    num_cols = 2
    for i in range(num_rows):
        row = st.columns(num_cols)
        for j in range(num_cols):
            idx = i * num_cols + j
            if idx < len(recommended_movies):
                with row[j]:
                    st.markdown(
                        f"""
                        <div style="background-color: rgba(255, 99, 71, 0.1); border-radius: 1%; height: 300px; display: flex; align-items: center; margin-bottom: 10px; margin-left: 100px; margin-right: 100px;">
                            <div style="flex: 0 0 200px;">
                                <img src="{recommended_posters[idx]}" style="width: 200px; height: auto;" />
                            </div>
                            <div style="flex: 1; padding-top: 10px; padding-left: 10px; padding-right: 10px; display: flex; flex-direction: column; margin-bottom: auto;">
                                <div>
                                    <p style="margin: 0; color: white;">
                                        <strong style="color: green;">Title: </strong> {recommended_movies[idx]}
                                    </p>
                                        <p style="margin: 0; color: white;">
                                    <strong style="color: green;">Genres: </strong> {recommended_genres[idx]}
                                    </p>
                                    <p style="margin: 0; color: white;">
                                        <strong style="color: green;">Director: </strong> {recommended_directors[idx]}
                                    </p>
                                    <p style="margin: 0; color: white;">
                                        <strong style="color: green;">Actors: </strong> {recommended_actors[idx]}
                                    </p>
                                </div>
                                <div style="margin-top: 20px;">
                                    <a type="button" href="{recommended_links[idx]}" style="background-color: green; color: white; padding: 10px 15px; text-decoration: none; border-radius: 20px; box-shadow: 1px 1px;"> Details </a>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
else:
    pass

# Add a footer using HTML and CSS
footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(251, 218, 97, 0.5); /* Adjust transparency here */
        background-image: linear-gradient(45deg, rgba(251, 218, 97, 0.5) 10%, rgba(255, 90, 205, 0.5) 70%);
        color: white;
        text-align: center;
        padding: 20px;
        font-size: 20px;
        z-index: 100;
    }
    </style>
    <div class="footer">
        <p>Powered by Streamlit | © 2024 KUN RATHA KEAN</p>
    </div>
"""

# Display the footer
st.markdown(footer, unsafe_allow_html=True)
