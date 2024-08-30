from flask import Blueprint, jsonify, request, render_template, redirect, url_for, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Movie, Review
from datamanager.init_db import init_database
from ai_functions import get_movie_recommendations, generate_movie_review, generate_movie_trivia
from movie_utils import fetch_movie_data
import logging
import traceback

api = Blueprint('api', __name__)

DB_FILE_NAME = 'moviwebapp.db'
engine = create_engine(f'sqlite:///{DB_FILE_NAME}')
Session = sessionmaker(bind=engine)

logger = logging.getLogger(__name__)


@api.route('/users', methods=['GET'])
def get_users():
    try:
        session = Session()
        users = session.query(User).all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        logger.error(f"Error in get_users: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while fetching users'}), 500
    finally:
        session.close()


@api.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    try:
        session = Session()
        user = session.query(User).get(user_id)
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        movies = user.movies
        return jsonify([movie.to_dict() for movie in movies])
    except Exception as e:
        logger.error(f"Error in get_user_movies: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while fetching user movies'}), 500
    finally:
        session.close()


@api.route('/users', methods=['POST'])
def create_user():
    try:
        session = Session()
        data = request.json
        new_user = User(name=data['name'])
        session.add(new_user)
        session.commit()
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        logger.error(f"Error in create_user: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while creating the user'}), 500
    finally:
        session.close()


@api.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    try:
        session = Session()
        data = request.json
        movie_data = fetch_movie_data(data['title'], data['year'])
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
            return jsonify(new_movie.to_dict()), 201
        else:
            return jsonify({'error': 'Movie not found'}), 404
    except Exception as e:
        logger.error(f"Error in add_movie: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while adding the movie'}), 500
    finally:
        session.close()


@api.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    try:
        session = Session()
        movie = session.query(Movie).get(movie_id)
        if movie is None:
            return jsonify({'error': 'Movie not found'}), 404
        data = request.json
        movie.name = data.get('name', movie.name)
        movie.year = data.get('year', movie.year)
        movie.director = data.get('director', movie.director)
        movie.rating = data.get('rating', movie.rating)
        session.commit()
        return jsonify(movie.to_dict())
    except Exception as e:
        logger.error(f"Error in update_movie: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while updating the movie'}), 500
    finally:
        session.close()


@api.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    try:
        session = Session()
        movie = session.query(Movie).get(movie_id)
        if movie is None:
            return jsonify({'error': 'Movie not found'}), 404
        session.delete(movie)
        session.commit()
        return jsonify({'message': 'Movie deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error in delete_movie: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while deleting the movie'}), 500
    finally:
        session.close()


@api.route('/users/<int:user_id>/recommendations', methods=['GET'])
def get_movie_recommendations(user_id):
    try:
        session = Session()
        user = session.query(User).get(user_id)
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        movies = user.movies
        movie_titles = [movie.name for movie in movies]
        recommendations = get_movie_recommendations(movie_titles)
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error in get_movie_recommendations: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while getting movie recommendations'}), 500
    finally:
        session.close()


@api.route('/movies/<int:movie_id>/review', methods=['GET'])
def get_ai_movie_review(movie_id):
    try:
        session = Session()
        movie = session.query(Movie).get(movie_id)
        if movie is None:
            return jsonify({'error': 'Movie not found'}), 404
        review = generate_movie_review(movie.name)
        return jsonify({'movie': movie.to_dict(), 'review': review})
    except Exception as e:
        logger.error(f"Error in get_ai_movie_review: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while getting the AI movie review'}), 500
    finally:
        session.close()


@api.route('/movies/<int:movie_id>/trivia', methods=['GET'])
def get_movie_trivia(movie_id):
    try:
        session = Session()
        movie = session.query(Movie).get(movie_id)
        if movie is None:
            return jsonify({'error': 'Movie not found'}), 404
        trivia = generate_movie_trivia(movie.name)
        return jsonify({'movie': movie.to_dict(), 'trivia': trivia})
    except Exception as e:
        logger.error(f"Error in get_movie_trivia: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while getting movie trivia'}), 500
    finally:
        session.close()
