from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import hashlib
import datetime
import correlation

engine = create_engine("sqlite:///ratings.db", echo = False)
session = scoped_session(sessionmaker(bind = engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

### Class declarations go here

class Compare:

    def similarity(self, other):
        user_ratings = {}
        # this will be a list of the ratings both self and other (user) have made where they match for the same movie
        paired_ratings = []
        for one_rating in self.ratings:
            # here we are putting a rating into our dictionary (the key is the movie title) and the value is the rating object (from our list)
            if isinstance(self, User):
                user_ratings[one_rating.movie_id] = one_rating
            if isinstance(self, Movie):
                user_ratings[one_rating.user_id] = one_rating

        for a_rating in other.ratings:
            # for each rating of the other user, check to see if our user has rated it (aka it's in the dictionary we just made.) this is our "rating buddy". If it's there, it'll be a rating object.
            if isinstance(self, User):
                rating_buddy = user_ratings.get(a_rating.movie_id)
            if isinstance(self, Movie):
                rating_buddy = user_ratings.get(a_rating.user_id)
            # if we have a match (rating buddy), append that to our list of pairs/matches (aka both you and the other user rated this movie)
            if rating_buddy:
                paired_ratings.append((rating_buddy.rating, a_rating.rating))
        # if we have any paired ratings, pass them to the pearson correlation
        if paired_ratings:
            return correlation.pearson(paired_ratings)
        # otherwise return 0 (no correlation?)
        else:
            return 0.0

class User(Base, Compare):
    __tablename__ = "users"

    id = Column(Integer(), primary_key = True)
    email = Column(String(64), nullable=True)
    password = Column(String(64), nullable = True)
    age = Column(Integer(),nullable = True)
    zipcode = Column(String(15), nullable=True)


    def predict_rating(self, movie):
        # my_ratings = self.ratings
        other_ratings = movie.ratings
        # find the similaritiy b/t yourself and the other user for a_rating (in other_ratings), then put the similarity number and the rating itself in a tuple and put it in the similarities list
        similarities = [(self.similarity(a_rating.user), a_rating) for a_rating in other_ratings]
        # reverse=True puts the larger elements at the beginning of the list
        similarities.sort(reverse=True)
        # rewrite the list with only positive (>0) similarity scores so that later when we multiply, we stay within 1-5 range.
        similarities = [similar for similar in similarities if similar[0] > 0]
        if not similarities:
            return None
        # multiply the rating * similarity score for all the tuples in similarities, then sum those.
        numerator = sum([a_rating.rating * similarity for similarity, a_rating in similarities])
        # sum all the similarity scores
        denominator = sum([similarity[0] for similarity in similarities])
        return numerator/denominator

    def predict_rating_with_my_movies(self, movie):
        # take all the movies you've rated and find out which movie this movie is most similar to
        # multiply your rating of that movie by the similarity of that movie
        
        my_ratings = self.ratings
        # returns a list of tuples of all rating pairs (similarity score for 2 movies, rating)
        # similarities = [ movie.similarity(a_rating.movie) for a_rating in my_ratings ]

        if self.ratings:
            similarities = []
            for a_rating in my_ratings:
                # get the similarity score for each movie you've rated compared to movie
                similarities.append( (movie.similarity(a_rating.movie), a_rating.movie, a_rating.rating) )

            similarities.sort(reverse=True)
            # print "this is similarities before we take out negatives", similarities
            # similarities = [similar for similar in similarities if similar[0] > 0]
            # if not similarities:
            #     print "returning none"
            #     return None
            # numerator = sum([a_rating.rating * similarity for similarity, a_rating in similarities])
            # denominator = sum([similarity[0] for similarity in similarities])
            # return numerator/denominator
            most_similar = similarities[0][1]
            most_similar_rating = similarities[0][2]

            return most_similar_rating * movie.similarity(most_similar)
        else:
            return 0


class Movie(Base, Compare):
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

def get_all_movies():
    movies = session.query(Movie).limit(10).all()
    return movies

def update_rating(inp_user_id, inp_movie_id, inp_rating):
    is_rated = session.query(Rating).filter_by(user_id=inp_user_id, movie_id=inp_movie_id).first()

    if is_rated:
        # update the rating to the new rating
        is_rated.rating=inp_rating
    else:
        # add new rating object
        rating = Rating(user_id=inp_user_id, movie_id=inp_movie_id, rating=inp_rating, timestamp = datetime.datetime.now())
        session.add(rating)

    session.commit()

def get_rating_movie_user(inp_user_id, inp_movie_id):
    rating = session.query(Rating).filter_by(user_id=inp_user_id, movie_id=inp_movie_id).first()
    return rating

def search_by_title(title):
    title_search = session.query(Movie).filter(Movie.movie_title.like("%"+title+"%")).all()
    return title_search

def judgment(user_id, movie_id):
    user = session.query(User).filter_by(id=user_id).first()
    movie = session.query(Movie).filter_by(id=movie_id).first()
    user_rating = session.query(Rating).filter_by(movie_id=movie_id,user_id=user_id).first()

    prediction = None
    prediction_when_not_rated = None

    if not user_rating:
        prediction = user.predict_rating_with_my_movies(movie)
        effective_rating = prediction
        prediction_when_not_rated = effective_rating
    else:
        effective_rating = user_rating.rating

    
    the_eye = session.query(User).filter_by(email="theeye@ofjudgment.com").one()
    eye_rating = session.query(Rating).filter_by(user_id=the_eye.id, movie_id=movie.id).first()

    if not eye_rating:
        eye_rating = the_eye.predict_rating(movie)
    else:
        eye_rating = eye_rating.rating

    difference = abs(eye_rating - effective_rating)

    messages = [ "I suppose you don't have such bad taste after all.",
             "I regret every decision that I've ever made that has brought me to listen to your opinion.",
             "Words fail me, as your taste in movies has clearly failed you.",
             "That movie is great. For a clown to watch. Idiot.",
             "You are the worst person to ever live."]

    print difference

    beratement = messages[int(difference)]

    return beratement, prediction_when_not_rated

def rounding(decimal):
    base = int(decimal)
    if decimal - base >= 0.5:
        return base+1
    else:
        return base

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
