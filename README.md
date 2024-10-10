# Movie Recommendation System 🎬

This project is a movie recommendation web application built with **Streamlit**. The app allows users to select a movie and receive recommendations based on similarity using **K-Nearest Neighbors (KNN)** and **TF-IDF** vectorization of movie metadata. Additionally, the app integrates with **The Movie Database (TMDb)** API to fetch movie details, posters, and more.

## Features
- **Random Movie Posters**: Displays a set of random movie posters on page load.
- **Movie Recommendations**: Allows users to select a movie and receive recommendations based on movie metadata.
- **Gradient Navbar and Custom Styling**: The app includes a customized gradient navbar and background styling using CSS.
- **Responsive Design**: The layout adapts to different screen sizes, making the application accessible across devices.
- **Integrated with TMDb API**: Fetches movie posters, director, actors, and IMDb links dynamically using TMDb API.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/kunratha/film_recommendation_ML_Streamlit.git
cd film_recommendation_ML_Streamlit
```

### 2. Create a Virtual Environment
You can create a virtual environment using venv:
**python3 -m venv venv**

### 3. Activate the Virtual Environment
#### On Windows:
**venv\Scripts\activate**

#### On Mac/Linux:
**source venv/bin/activate**

### 4. Install Dependencies
Make sure all required packages are installed by running:
**pip install -r requirements.txt**

### 5. Set Up TMDb API Key

**API_KEY = "your_api_key_here"**

### 6. Run the Application
**streamlit run home.py**

# File Structure
Go to TMDb and create an account.
**Generate your API key and replace it in the API_KEY.**
├── home.py               # Main application code
├── movies_list.pkl        # Pre-processed movie metadata
├── knn_model.pkl          # Pre-trained KNN model for recommendations
├── tfidf_vectorizer.pkl   # TF-IDF Vectorizer for movie metadata
├── requirements.txt       # Dependencies
├── README.md              # This readme file
└── assets                 # Directory for static assets (posters, etc.)
variable in the home.py file.

# Requirements
- **Python 3.7+**
- **Streamlit**
- **Scikit-learn**
- **Requests (for fetching data from TMDb API)**
- **Pickle (for loading pre-trained models)**


# How It Works
- **The TF-IDF Vectorizer converts movie metadata (tags) into numerical format.**
- **The KNN model finds similar movies based on the vectorized data.**
- **The app interacts with TMDb API to fetch movie posters, cast, and director details.**
- **A set of movie posters is displayed at the top of the page upon loading.**

# API Integration
This project uses The Movie Database (TMDb) API to fetch movie posters, cast, and additional movie information. The API provides detailed movie information such as:

- **Poster Images**
- **Movie Overview**
- **Director**
- **Actors**
- **IMDb Links**

# License
This project is licensed under the MIT License.

*Feel free to copy and paste this text into your `README.md` file. 
It provides an overview of your project, features, installation steps, and instructions for using the app!*

    Users can s instructions for using the app!elect a movie, and the app will return a list of similar movies, displayed along with their posters and metadata.
