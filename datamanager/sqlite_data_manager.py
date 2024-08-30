import sqlite3
from datamanager.data_manager_interface import DataManagerInterface


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def get_all_users(self):
        self.cursor.execute("SELECT * FROM users")
        return [{'id': row[0], 'name': row[1]} for row in self.cursor.fetchall()]

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = self.cursor.fetchone()
        if user:
            return {'id': user[0], 'name': user[1]}
        return None

    def add_user(self, name):
        self.cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        self.conn.commit()

    def get_user_movies(self, user_id):
        self.cursor.execute("SELECT * FROM movies WHERE user_id = ?", (user_id,))
        return [{'id': row[0], 'name': row[2], 'year': row[3], 'director': row[4], 'rating': row[5], 'poster': row[6]}
                for row in self.cursor.fetchall()]

    def get_movie(self, movie_id):
        self.cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
        movie = self.cursor.fetchone()
        if movie:
            return {'id': movie[0], 'user_id': movie[1], 'name': movie[2], 'year': movie[3], 'director': movie[4],
                    'rating': movie[5], 'poster': movie[6]}
        return None

    def add_movie(self, user_id, movie_data):
        query = '''INSERT INTO movies (user_id, name, year, director, rating, poster)
                   VALUES (?, ?, ?, ?, ?, ?)'''
        self.cursor.execute(query, (user_id, movie_data['name'], movie_data['year'],
                                    movie_data['director'], movie_data['rating'], movie_data['poster']))
        self.conn.commit()

    def update_movie(self, movie_id, movie_data):
        query = '''UPDATE movies SET name = ?, year = ?, director = ?, rating = ?, poster = ?
                   WHERE id = ?'''
        self.cursor.execute(query, (movie_data['name'], movie_data['year'], movie_data['director'],
                                    movie_data['rating'], movie_data['poster'], movie_id))
        self.conn.commit()

    def delete_movie(self, movie_id):
        self.cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
