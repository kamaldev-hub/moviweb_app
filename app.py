from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Movie, Review
from datamanager.init_db import init_database
from api import api  # Import the Blueprint from the new api.py
from ai_functions import get_movie_recommendations, generate_movie_review, generate_movie_trivia
from movie_utils import fetch_movie_data
import logging
from dotenv import load_dotenv
import os
import traceback

load_dotenv()

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.static_folder = 'static'
DB_FILE_NAME = 'moviwebapp.db'

# Initialize the database
init_database(DB_FILE_NAME)

# Set up SQLAlchemy
engine = create_engine(f'sqlite:///{DB_FILE_NAME}')
Session = sessionmaker(bind=engine)

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/users')
def list_users():
    try:
        session = Session()
        users = session.query(User).all()
        return render_template('users.html', users=users)
    except Exception as e:
        logger.error(f"Error in list_users: {str(e)}")
        logger.error(traceback.format_exc())
        abort(500)
    finally:
        session.close()


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    try:
        session = Session()
        user = session.query(User).get(user_id)
        if user is None:
            logger.warning(f"User not found: {user_id}")
            abort(404)
        movies = user.movies
        logger.info(f"Found {len(movies)} movies for user {user_id}")
        for movie in movies:
            logger.info(f"Movie: {movie.name}, Poster: {movie.poster}, Poster type: {type(movie.poster)}")
        return render_template('user_movies.html', user=user, movies=movies)
    except Exception as e:
        logger.error(f"Error in user_movies: {str(e)}")
        logger.error(traceback.format_exc())
        abort(500)
    finally:
        session.close()


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            session = Session()
            name = request.form['name']
            new_user = User(name=name)
            session.add(new_user)
            session.commit()
            return redirect(url_for('list_users'))
        except Exception as e:
            logger.error(f"Error in add_user: {str(e)}")
            logger.error(traceback.format_exc())
            return render_template('add_user.html', error="An error occurred while adding the user.")
        finally:
            session.close()
    return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        try:
            session = Session()
            movie_data = fetch_movie_data(request.form['title'])
            if movie_data:
                new_movie = Movie(
                    name=movie_data['name'],
                    year=movie_data['year'],
                    director=movie_data['director'],
                    rating=movie_data['rating'],
                    poster=movie_data['poster'],
                    user_id=user_id
                )
                session.add(new_movie)
                session.commit()
                logger.info(f"Added new movie: {new_movie.name}, Poster: {new_movie.poster}")
                return redirect(url_for('user_movies', user_id=user_id))
            else:
                return render_template('add_movie.html', user_id=user_id, error="Movie not found")
        except Exception as e:
            logger.error(f"Error in add_movie: {str(e)}")
            logger.error(traceback.format_exc())
            return render_template('add_movie.html', user_id=user_id, error="An error occurred while adding the movie.")
        finally:
            session.close()
    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    try:
        session = Session()
        movie = session.query(Movie).get(movie_id)
        if movie is None:
            logger.warning(f"Movie not found: {movie_id}")
            abort(404)
        if request.method == 'POST':
            movie.name = request.form['title']
            movie.year = int(request.form['year'])
            movie.director = request.form['director']
            movie.rating = float(request.form['rating'])
            session.commit()
            return redirect(url_for('user_movies', user_id=user_id))
        return render_template('update_movie.html', user_id=user_id, movie=movie)
    except Exception as e:
        logger.error(f"Error in update_movie: {str(e)}")
        logger.error(traceback.format_exc())
        abort(500)
    finally:
        session.close()


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    try:
        session = Session()
        movie = session.query(Movie).get(movie_id)
        if movie:
            session.delete(movie)
            session.commit()
        return redirect(url_for('user_movies', user_id=user_id))
    except Exception as e:
        logger.error(f"Error in delete_movie: {str(e)}")
        logger.error(traceback.format_exc())
        abort(500)
    finally:
        session.close()


@app.route('/users/<int:user_id>/recommendations')
def movie_recommendations(user_id):
    try:
        session = Session()
        user = session.query(User).get(user_id)
        if user is None:
            logger.warning(f"User not found: {user_id}")
            abort(404)
        movies = user.movies
        movie_titles = [movie.name for movie in movies]
        recommendations = get_movie_recommendations(movie_titles)
        return render_template('recommendations.html', user=user, recommendations=recommendations)
    except Exception as e:
        logger.error(f"Error in movie_recommendations: {str(e)}")
        logger.error(traceback.format_exc())
        abort(500)
    finally:
        session.close()


@app.route('/movies/<int:movie_id>/review')
def ai_movie_review(movie_id):
    try:
        session = Session()
        movie = session.query(Movie).get(movie_id)
        if movie is None:
            logger.warning(f"Movie not found: {movie_id}")
            abort(404)
        review = generate_movie_review(movie.name)
        return render_template('ai_review.html', movie=movie, review=review)
    except Exception as e:
        logger.error(f"Error in ai_movie_review: {str(e)}")
        logger.error(traceback.format_exc())
        abort(500)
    finally:
        session.close()


@app.route('/movies/<int:movie_id>/trivia')
def movie_trivia(movie_id):
    try:
        session = Session()
        movie = session.query(Movie).get(movie_id)
        if movie is None:
            logger.warning(f"Movie not found: {movie_id}")
            abort(404)
        trivia = generate_movie_trivia(movie.name)
        return render_template('movie_trivia.html', movie=movie, trivia=trivia)
    except Exception as e:
        logger.error(f"Error in movie_trivia: {str(e)}")
        logger.error(traceback.format_exc())
        abort(500)
    finally:
        session.close()


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    try:
        session = Session()
        user = session.query(User).get(user_id)
        if user is None:
            logger.warning(f"User not found: {user_id}")
            return redirect(url_for('list_users'))

        # Delete all movies associated with the user
        session.query(Movie).filter_by(user_id=user_id).delete()

        # Delete the user
        session.delete(user)
        session.commit()
        logger.info(f"User {user_id} and associated movies deleted successfully.")
        return redirect(url_for('list_users'))
    except Exception as e:
        logger.error(f"Error in delete_user: {str(e)}")
        logger.error(traceback.format_exc())
        session.rollback()
        return redirect(url_for('list_users'))
    finally:
        session.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)