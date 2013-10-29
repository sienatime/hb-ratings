from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import hashlib

engine = create_engine("sqlite:///ratings.db", echo = False)
session = scoped_session(sessionmaker(bind = engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

### Class declarations go here

class User(Base):
    __tablename__ = "users"

    id = Column(Integer(), primary_key = True)
    email = Column(String(64), nullable=True)
    password = Column(String(64), nullable = True)
    age = Column(Integer(),nullable = True)
    zipcode = Column(String(15), nullable=True)

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer(), primary_key = True)
    movie_title = Column(String(64), nullable = True)
    release_date = Column(DateTime(), nullable = True)
    imdb_url = Column(String(100), nullable=True)

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer(), primary_key = True)
    user_id = Column(Integer(), ForeignKey('users.id'), nullable=True)
    movie_id = Column(Integer(), ForeignKey('movies.id'), nullable=True)
    rating = Column(Integer(), nullable=True)
    timestamp = Column(DateTime(), nullable=True)

    user = relationship("User",
        backref=backref("ratings", order_by=id))

    movie = relationship("Movie",
        backref=backref("ratings", order_by=id))

### End class declarations

def add_user(inp_email, inp_password, inp_age, inp_zipcode):
    user = User(email=inp_email, password=md5_hash(inp_password), age=inp_age, zipcode=inp_zipcode)
    session.add(user)
    session.commit()

def is_user(inp_email):
    user = session.query(User).filter_by(email=inp_email).all()
    return user

def md5_hash(password):
    return hashlib.md5(password).hexdigest()

def auth_match(inp_email, inp_password):
    user = session.query(User).filter_by(email=inp_email, password=md5_hash(inp_password)).one()
    return user

def get_id_by_email(inp_email):
    user = session.query(User).filter_by(email=inp_email).one()
    return user.id

def get_email_by_id(inp_id):
    email = session.query(User).filter_by(id=inp_id).one()
    return email

def get_ratings_from_user(userid):
    ratings = session.query(Rating).filter_by(user_id=userid).all()
    return ratings

def get_ratings_for_movie(inp_movie):
    ratings = session.query(Rating).filter_by(movie_id=inp_movie).all()
    return ratings

def get_movie_title_from_id(inp_movie_id):
    movie_title = session.query(Movie).filter_by(id=inp_movie_id).one()
    return movie_title.movie_title

def get_all_users():
    users = session.query(User).limit(5).all()
    return users

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
