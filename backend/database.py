import os 
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/resume_app')

# Create engine with proper configuration
engine = create_engine(
    DATABASE_URL, 
    echo=True,  # Set to False in production
    pool_pre_ping=True,
    pool_recycle=300
)

def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)
    print("✓ Database tables created successfully")

def get_session():
    """Dependency for getting database sessions"""
    with Session(engine) as session:
        yield session

def test_connection():
    """Test database connection"""
    try: 
        with Session(engine) as session:
            result = session.exec('SELECT 1').first()
            print('✓ Database connection successful')
            return True
    except Exception as e: 
        print(f'✗ Database connection failed: {e}')
        return False

if __name__ == '__main__':
    test_connection()