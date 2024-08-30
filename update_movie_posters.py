from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Movie
from movie_utils import fetch_movie_data

DB_FILE_NAME = 'moviwebapp.db'
engine = create_engine(f'sqlite:///{DB_FILE_NAME}')
Session = sessionmaker(bind=engine)

def update_movie_posters():
    session = Session()
    movies = session.query(Movie).all()
    for movie in movies:
        if not movie.poster:
            movie_data = fetch_movie_data(movie.name, movie.year)
            if movie_data and movie_data['poster']:
                movie.poster = movie_data['poster']
                print(f"Updated poster for {movie.name}: {movie.poster}")
    session.commit()
    session.close()

if __name__ == "__main__":
    update_movie_posters()