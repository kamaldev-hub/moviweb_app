from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    movies = relationship("Movie", back_populates="user")
    reviews = relationship("Review", back_populates="user")


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    year = Column(Integer)
    director = Column(String(100))
    rating = Column(Float)
    poster = Column(String(300))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="movies")
    reviews = relationship("Review", back_populates="movie")


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    user = relationship("User", back_populates="reviews")
    movie = relationship("Movie", back_populates="reviews")
