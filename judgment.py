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
            redirect(url_for("signin"))
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
        return render_template("home.html")
    else:
        flash("Your email and password didn't match our records. Please sign in.")
        return redirect(url_for("signin"))

@app.route("/all_users")
def get_users():
    user_list = model.get_all_users()
    return render_template("user_list.html", users=user_list)

@app.route("/user/<user_id>")
def get_profile(user_id):
    ratings = model.get_ratings_from_user(user_id)
    return render_template("ratings.html", ratings=ratings, profile=user_id)

@app.route("/movie/<movie_id>")
def show_movie(movie_id):
    ratings = model.get_ratings_for_movie(movie_id)
    movie_title = model.get_movie_title_from_id(movie_id)

    all_sum = 0
    count = 0
    for rating in ratings:
        all_sum += rating.rating
        count += 1

    avg = float(all_sum)/count

    return render_template("movie.html", avg=avg, movie_title=movie_title)

if __name__ == "__main__":
    app.run(debug = True)