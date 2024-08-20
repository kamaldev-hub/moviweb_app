from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Movie, Review


class SQLiteDataManager:
    def __init__(self, db_file_name):
        self.engine = create_engine(f'sqlite:///{db_file_name}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_all_users(self):
        session = self.Session()
        users = session.query(User).all()
        session.close()
        return users

    def get_user(self, user_id):
        session = self.Session()
        user = session.query(User).get(user_id)
        session.close()
        return user

    def add_user(self, name):
        session = self.Session()
        new_user = User(name=name)
        session.add(new_user)
        session.commit()
        session.close()

    def get_user_movies(self, user_id):
        session = self.Session()
        movies = session.query(Movie).filter_by(user_id=user_id).all()
        session.close()
        return movies

    def add_movie(self, user_id, movie_data):
        session = self.Session()
        new_movie = Movie(user_id=user_id, **movie_data)
        session.add(new_movie)
        session.commit()
        session.close()

    def get_movie(self, movie_id):
        session = self.Session()
        movie = session.query(Movie).get(movie_id)
        session.close()
        return movie

    def update_movie(self, movie_id, movie_data):
        session = self.Session()
        movie = session.query(Movie).get(movie_id)
        if movie:
            for key, value in movie_data.items():
                setattr(movie, key, value)
            session.commit()
        session.close()

    def delete_movie(self, movie_id):
        session = self.Session()
        movie = session.query(Movie).get(movie_id)
        if movie:
            session.delete(movie)
            session.commit()
        session.close()

    def add_review(self, user_id, movie_id, review_text, rating):
        session = self.Session()
        new_review = Review(text=review_text, rating=rating, user_id=user_id, movie_id=movie_id)
        session.add(new_review)
        session.commit()
        session.close()

    def get_movie_reviews(self, movie_id):
        session = self.Session()
        reviews = session.query(Review).filter_by(movie_id=movie_id).all()
        session.close()
        return reviews

    def get_review(self, review_id):
        session = self.Session()
        review = session.query(Review).get(review_id)
        session.close()
        return review

    def update_review(self, review_id, review_text, rating):
        session = self.Session()
        review = session.query(Review).get(review_id)
        if review:
            review.text = review_text
            review.rating = rating
            session.commit()
        session.close()

    def delete_review(self, review_id):
        session = self.Session()
        review = session.query(Review).get(review_id)
        if review:
            session.delete(review)
            session.commit()
        session.close()
