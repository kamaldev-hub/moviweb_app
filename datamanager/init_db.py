from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Movie


def init_database(db_file_name='moviwebapp.db'):
    engine = create_engine(f'sqlite:///{db_file_name}')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Add some initial data if the database is empty
    if session.query(User).count() == 0:
        user1 = User(name="John Doe")
        user2 = User(name="Jane Smith")
        session.add(user1)
        session.add(user2)
        session.commit()

        movie1 = Movie(name="Inception", year=2010, director="Christopher Nolan", rating=8.8, user_id=user1.id)
        movie2 = Movie(name="The Shawshank Redemption", year=1994, director="Frank Darabont", rating=9.3,
                       user_id=user1.id)
        movie3 = Movie(name="The Godfather", year=1972, director="Francis Ford Coppola", rating=9.2, user_id=user2.id)
        session.add_all([movie1, movie2, movie3])
        session.commit()

    session.close()


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")