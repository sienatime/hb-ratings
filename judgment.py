from flask import Flask, render_template, flash, request, redirect, url_for, session
import model
app = Flask(__name__)
app.secret_key = "yosecretkey"

@app.route("/")
def index():
    if session.get('email'):
        return render_template("home.html")
    else:
        return redirect(url_for("register"))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=['POST'])
def new_user():
    email = request.form.get("email")
    pwd = request.form.get("password")
    verify_pwd = request.form.get("password_verify")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")

    if (pwd == verify_pwd) and (email and pwd and age and zipcode):
        if model.is_user(email):
            flash("You're already registered. Please sign in.")
            return redirect(url_for("signin"))
        else:
            model.add_user(email, pwd, age, zipcode)
            flash("Thanks for registering! Please sign in.","success")
            return redirect(url_for("signin"))
    elif pwd != verify_pwd:
        flash("Passwords must match.","error")
        return redirect(url_for("register"))
    else:
        flash("All fields are required.","error")
        return redirect(url_for("register"))

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/signin", methods=['POST'])
def sign_in():
    email = request.form.get("email")
    pwd = request.form.get("password")

    if model.auth_match(email, pwd):
        flash("Signed in.")
        session['email'] = email
        session['user_id'] = model.get_id_by_email(email)
        return redirect(url_for("get_profile", user_id=session['user_id']))
    else:
        flash("Your email and password didn't match our records. Please sign in.")
        return redirect(url_for("signin"))

@app.route("/all_users")
def get_users():
    user_list = model.get_all_users(0)
    return render_template("user_list.html", users=user_list)

@app.route("/more_users/<offset>")
def get_more_users(offset):
    user_list = model.get_all_users(int(offset))
    return render_template("more_users.html", users=user_list)

@app.route("/user/<user_id>")
def get_profile(user_id):
    ratings = model.get_ratings_from_user(user_id)
    return render_template("ratings.html", ratings=ratings, profile=user_id)

@app.route("/movie/<movie_id>")
def show_movie(movie_id):
    ratings = model.get_ratings_for_movie(movie_id)
    movie_object = model.get_movie(movie_id)

    all_sum = 0
    count = 0
    for rating in ratings:
        all_sum += rating.rating
        count += 1

    avg = float(all_sum)/count

    avg = model.rounding(avg)

    rated = None

    if session.get('user_id'):
        rated = model.get_rating_movie_user(session['user_id'], movie_id)

    return render_template("movie.html", avg=avg, movie_object=movie_object, rated=rated)

@app.route("/getjudgment")
def get_judgment():
    if session.get('user_id'):
        movie_id = request.args.get('movie_id')

        judgy, prediction = model.judgment(session['user_id'], movie_id)

        if prediction:
            prediction = model.rounding(prediction)

        return render_template("ajaxy.html", prediction=prediction, judgy=judgy)
    else:
        return "Register to see what the eye has to say about your taste in movies!"

@app.route("/all_movies")
def get_movies():
    movie_list = model.get_all_movies(0)
    return render_template("movies.html", movies=movie_list)

@app.route("/more_movies/<offset>")
def get_more_movies(offset):
    movie_list = model.get_all_movies(int(offset))
    return render_template("more_movies.html", movies=movie_list)

@app.route("/rate", methods=["POST"])
def rate_movie():
    user_id = session['user_id']
    movie_id = request.form.get("movie_id")
    rating = request.form.get("rating")

    model.update_rating(user_id, movie_id, rating)
    return redirect(url_for("show_movie",movie_id=movie_id))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/searchresults")
def search_movies():
    title = request.args.get("search")
    results = model.search_by_title(title)

    if len(results) == 1:
        movie_id = results[0].id
        return redirect(url_for("show_movie",movie_id=movie_id))
    else:
        return render_template("results.html", results=results)

if __name__ == "__main__":
    app.run(debug = True)