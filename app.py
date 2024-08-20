from flask import Flask, render_template, request, redirect, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager
import requests

app = Flask(__name__)
data_manager = SQLiteDataManager('moviwebapp.db')
OMDB_API_KEY = 'c94f02ef'


@app.route('/')
def home():
    return "Welcome to MovieWeb App!"


@app.route('/users')
def list_users():
    users = data_manager.list_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    user = data_manager.get_user(user_id)
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user=user, movies=movies)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        data_manager.add_user(name)
        return redirect(url_for('list_users'))
    return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        # Fetch movie details from OMDb API
        response = requests.get(f'http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}&y={year}')
        movie_data = response.json()

        if movie_data['Response'] == 'True':
            movie = {
                'name': movie_data['Title'],
                'year': movie_data['Year'],
                'director': movie_data['Director'],
                'rating': movie_data['imdbRating']
            }
            data_manager.add_movie(user_id, movie)
            return redirect(url_for('user_movies', user_id=user_id))
        else:
            error = "Movie not found"
            return render_template('add_movie.html', user_id=user_id, error=error)

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    movie = data_manager.get_movie(movie_id)
    if request.method == 'POST':
        movie['name'] = request.form['title']
        movie['year'] = request.form['year']
        movie['director'] = request.form['director']
        movie['rating'] = request.form['rating']
        data_manager.update_movie(movie_id, movie)
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('update_movie.html', user_id=user_id, movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


if __name__ == '__main__':
    app.run(debug=True)