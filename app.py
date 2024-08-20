from flask import Flask, render_template, request, redirect, url_for, abort
from datamanager.sqlite_data_manager import SQLiteDataManager
from datamanager.init_db import init_database
from api import api  # Import the API blueprint
import requests
import logging

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')  # Register the API blueprint
app.static_folder = 'static'
DB_FILE_NAME = 'moviwebapp.db'
OMDB_API_KEY = 'c94f02ef'

# Initialize the database and data manager
init_database(DB_FILE_NAME)
data_manager = SQLiteDataManager(DB_FILE_NAME)

# Set up logging to output to console
logging.basicConfig(level=logging.INFO)
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
        users = data_manager.get_all_users()
        return render_template('users.html', users=users)
    except Exception as e:
        logger.error(f"Error in list_users: {str(e)}")
        abort(500)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    try:
        user = data_manager.get_user(user_id)
        if user is None:
            abort(404)
        movies = data_manager.get_user_movies(user_id)
        return render_template('user_movies.html', user=user, movies=movies)
    except Exception as e:
        logger.error(f"Error in user_movies: {str(e)}")
        abort(500)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            name = request.form['name']
            data_manager.add_user(name)
            return redirect(url_for('list_users'))
        except Exception as e:
            logger.error(f"Error in add_user: {str(e)}")
            return render_template('add_user.html', error="An error occurred while adding the user.")
    return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        try:
            movie_data = fetch_movie_data(request.form['title'], request.form['year'])
            if movie_data:
                data_manager.add_movie(user_id, movie_data)
                return redirect(url_for('user_movies', user_id=user_id))
            else:
                return render_template('add_movie.html', user_id=user_id, error="Movie not found")
        except requests.RequestException as e:
            logger.error(f"Error in add_movie (API request): {str(e)}")
            return render_template('add_movie.html', user_id=user_id,
                                   error="An error occurred while fetching movie data.")
        except Exception as e:
            logger.error(f"Error in add_movie: {str(e)}")
            return render_template('add_movie.html', user_id=user_id, error="An error occurred while adding the movie.")
    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    try:
        movie = data_manager.get_movie(movie_id)
        if movie is None:
            abort(404)
        if request.method == 'POST':
            movie_data = {
                'name': request.form['title'],
                'year': request.form['year'],
                'director': request.form['director'],
                'rating': request.form['rating']
            }
            data_manager.update_movie(movie_id, movie_data)
            return redirect(url_for('user_movies', user_id=user_id))
        return render_template('update_movie.html', user_id=user_id, movie=movie)
    except Exception as e:
        logger.error(f"Error in update_movie: {str(e)}")
        abort(500)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    try:
        data_manager.delete_movie(movie_id)
        return redirect(url_for('user_movies', user_id=user_id))
    except Exception as e:
        logger.error(f"Error in delete_movie: {str(e)}")
        abort(500)


@app.route('/movies/<int:movie_id>/reviews')
def movie_reviews(movie_id):
    try:
        movie = data_manager.get_movie(movie_id)
        if movie is None:
            abort(404)
        reviews = data_manager.get_movie_reviews(movie_id)
        return render_template('movie_reviews.html', movie=movie, reviews=reviews)
    except Exception as e:
        logger.error(f"Error in movie_reviews: {str(e)}")
        abort(500)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/add_review', methods=['GET', 'POST'])
def add_review(user_id, movie_id):
    if request.method == 'POST':
        try:
            review_text = request.form['review_text']
            rating = float(request.form['rating'])
            data_manager.add_review(user_id, movie_id, review_text, rating)
            return redirect(url_for('movie_reviews', movie_id=movie_id))
        except Exception as e:
            logger.error(f"Error in add_review: {str(e)}")
            return render_template('add_review.html', user_id=user_id, movie_id=movie_id,
                                   error="An error occurred while adding the review.")
    return render_template('add_review.html', user_id=user_id, movie_id=movie_id)


@app.route('/reviews/<int:review_id>/update', methods=['GET', 'POST'])
def update_review(review_id):
    try:
        review = data_manager.get_review(review_id)
        if review is None:
            abort(404)
        if request.method == 'POST':
            review_text = request.form['review_text']
            rating = float(request.form['rating'])
            data_manager.update_review(review_id, review_text, rating)
            return redirect(url_for('movie_reviews', movie_id=review.movie_id))
        return render_template('update_review.html', review=review)
    except Exception as e:
        logger.error(f"Error in update_review: {str(e)}")
        abort(500)


@app.route('/reviews/<int:review_id>/delete')
def delete_review(review_id):
    try:
        review = data_manager.get_review(review_id)
        if review is None:
            abort(404)
        movie_id = review.movie_id
        data_manager.delete_review(review_id)
        return redirect(url_for('movie_reviews', movie_id=movie_id))
    except Exception as e:
        logger.error(f"Error in delete_review: {str(e)}")
        abort(500)


def fetch_movie_data(title, year):
    response = requests.get(f'http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}&y={year}')
    movie_data = response.json()
    if movie_data['Response'] == 'True':
        return {
            'name': movie_data['Title'],
            'year': movie_data['Year'],
            'director': movie_data['Director'],
            'rating': movie_data['imdbRating']
        }
    return None


if __name__ == '__main__':
    logger.info("Starting Flask app...")
    logger.info("Please navigate to http://127.0.0.1:5000/ in your web browser")
    app.run(debug=True)
