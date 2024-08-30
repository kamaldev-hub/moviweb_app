import os
import requests
from dotenv import load_dotenv

load_dotenv()

OMDB_API_KEY = os.getenv('OMDB_API_KEY')


def fetch_movie_data(title, year):
    response = requests.get(f'http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}&y={year}')
    movie_data = response.json()
    if movie_data['Response'] == 'True':
        return {
            'name': movie_data['Title'],
            'year': int(movie_data['Year']),
            'director': movie_data['Director'],
            'rating': float(movie_data['imdbRating']),
            'poster': movie_data['Poster']
        }
    return None
