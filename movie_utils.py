import os
import requests
from dotenv import load_dotenv

load_dotenv()

OMDB_API_KEY = os.getenv('OMDB_API_KEY')


def fetch_movie_data(title, year=None):
    base_url = 'http://www.omdbapi.com/'

    params = {
        'apikey': OMDB_API_KEY,
        't': title,
        'type': 'movie'
    }
    if year:
        params['y'] = year

    response = requests.get(base_url, params=params)
    movie_data = response.json()

    if movie_data.get('Response') == 'True':
        return {
            'name': movie_data['Title'],
            'year': int(movie_data['Year']),
            'director': movie_data['Director'],
            'rating': float(movie_data['imdbRating']) if movie_data['imdbRating'] != 'N/A' else 0.0,
            'poster': movie_data['Poster'] if movie_data['Poster'] != 'N/A' else None
        }
    return None
