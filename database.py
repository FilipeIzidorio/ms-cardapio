from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql://dbcardapio_w1xz_user:k6ZzjAQGBYUPwmubQRBFiRcCZgekjvSM@dpg-d39dl0ogjchc73dm9320-a.oregon-postgres.render.com/dbcardapio_w1xz"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
