from datamanager.data_manager_interface import DataManagerInterface
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file_name):
        self.engine = create_engine(f'sqlite:///{db_file_name}')
        self.Session = sessionmaker(bind=self.engine)

    def get_all_users(self):
        session = self.Session()
        users = session.query(User).all()
        session.close()
        return users

    # ... other methods ...
