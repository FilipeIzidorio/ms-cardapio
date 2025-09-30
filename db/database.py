from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "postgresql://ms_cardapio_db_user:AVkbWwF501JkkF8nhP1fkr1HMtkOJSHS@dpg-d3av2abuibrs73f2g6j0-a.oregon-postgres.render.com/ms_cardapio_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency para injeção no FastAPI
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
