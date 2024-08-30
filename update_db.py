from sqlalchemy import create_engine, text
from models import Base


def update_database(db_file_name='moviwebapp.db'):
    engine = create_engine(f'sqlite:///{db_file_name}')

    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE movies ADD COLUMN poster VARCHAR(300)"))
        conn.commit()

    print(f"Database updated: {db_file_name}")


if __name__ == "__main__":
    update_database()
    print("Database update completed successfully!")