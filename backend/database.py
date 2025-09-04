import os 
from sqlmodel import SQLModel, create_engine, Session 
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL= os.getenv('DATABASE_URL', 'postgresql://localhost:5432/resume_app')

engine = create_engine(
    DATABASE_URL, 
    echo = True,
    pool_pre_ping = True,
    pool_recycle = 300
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    return Session(engine)
  
        
def test_connections():
    try: 
        with Session(engine) as session:
            session.exec('SELECT 1')
        print('Database connection succsessful')
        return True
    except Exception as e: 
        print(f'Database connection failed: {e}')
        return False


if __name__ == '__main__':
    test_connections()    


