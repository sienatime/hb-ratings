import model
import csv
import datetime

def load_users(session):
    # use u.user
    f = open("seed_data/u.user")
    r = csv.reader(f, delimiter="|")

    for row in r:
        #do stuff
        data = row 
        #this is a list of data
        user = model.User(age= data[1], zipcode= data[4])
        session.add(user)
    session.commit()

def load_movies(session):
    # use u.item
    f = open("seed_data/u.item")
    r = csv.reader(f, delimiter="|")

    for row in r:
        data = row
        title = data[1]
        tokens = title.split("(")
        new_title = tokens[0].strip()
        decoded_title = new_title.decode("latin-1")
        rel_date =  data[2]

        if rel_date:
            new_date = datetime.datetime.strptime(rel_date, "%d-%b-%Y")
            movie = model.Movie(movie_title = decoded_title, release_date = new_date, imdb_url = data[4])
        else:
            movie = model.Movie(movie_title = decoded_title, imdb_url = data[4])
        
        session.add(movie)
    session.commit()

def load_ratings(session):
    # use u.data
    f = open("seed_data/u.data")
    r = csv.reader(f, delimiter= "\t")

    for row in r:
        data = row
        time = datetime.date.fromtimestamp(float(data[3]))
        rating = model.Rating(user_id = data[0], movie_id = data[1], rating = data[2], timestamp = time)
        session.add(rating)
    session.commit()


def main(session):
    # You'll call each of the load_* functions with the session as an argument
    load_users(session)
    load_movies(session)
    load_ratings(session)

if __name__ == "__main__":
    s= model.connect()
    main(s)
