from flask import Blueprint, jsonify, request
from datamanager.sqlite_data_manager import SQLiteDataManager

api = Blueprint('api', __name__)
data_manager = SQLiteDataManager('moviwebapp.db')

@api.route('/users', methods=['GET'])
def get_users():
    users = data_manager.get_all_users()
    return jsonify([{'id': user.id, 'name': user.name} for user in users])

@api.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    movies = data_manager.get_user_movies(user_id)
    return jsonify([{
        'id': movie.id,
        'name': movie.name,
        'year': movie.year,
        'director': movie.director,
        'rating': movie.rating
    } for movie in movies])

@api.route('/users/<int:user_id>/movies', methods=['POST'])
def add_user_movie(user_id):
    movie_data = request.json
    new_movie = data_manager.add_movie(user_id, movie_data)
    return jsonify({
        'id': new_movie.id,
        'name': new_movie.name,
        'year': new_movie.year,
        'director': new_movie.director,
        'rating': new_movie.rating
    }), 201