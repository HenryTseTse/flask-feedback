from flask import Flask, flash, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from forms import RegisterForm, LoginForm, FeedbackForm
from models import User, Feedback, connect_db, db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)
toolbar = DebugToolbarExtension(app)

@app.route("/")
def homepage():
    """Homepage Redirect Register"""
    return redirect("/register")

@app.route("/register", methods = ['GET', 'POST'])
def register():
    """Register A User"""

    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User.register(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
        )
        db.session.commit()
        session["username"] = new_user.username
        flash(f"Welcome {new_user.username}!", "danger")
        return redirect(f"/users/{new_user.username}")
    
    return render_template("/register.html", form=form)


@app.route("/login", methods = ['GET', 'POST'])
def login_form():
    """Login Form"""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        login_user = User.authenticate(
                username = form.username.data,
                password = form.password.data
        )
        if login_user:
            session['username'] = login_user.username
            return redirect(f"/users/{login_user.username}")
        else:
            form.username.errors = ["Invalid Username/Password"]
            return render_template("users/login.html", form=form)
    
    return render_template("/login.html", form=form)

@app.route("/users/<username>")
def display_user(username):
    if "username" not in session or username != session['username']:
        flash("Please Login First!", "danger")
        return redirect("/login")
    
    user = User.query.get(username)
    feedbacks = Feedback.query.filter_by(username=username).all()
    return render_template("/user_details.html", user=user, feedbacks=feedbacks)

@app.route("/logout")
def logout():
    session.pop("username")
    return redirect("/login")


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    if "username" not in session or username != session["username"]:
        flash("You don't have access to delete this account")
        return redirect("/login")
    
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    flash("Your account has been deleted")
    return redirect("/")

@app.route("/users/<username>/feedback/add", methods=["GET","POST"])
def add_feedback(username):
    if "username" not in session or username != session["username"]:
        flash("Please log in to access this feature", "danger")
        return redirect("/login")
    
    form = FeedbackForm()

    if form.validate_on_submit():
        new_feedback = Feedback(title=form.title.data, content=form.content.data, username=username)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(f"/users/{username}")
    
    return render_template("/feedback_form.html", form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=["GET","POST"])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session["username"]:
        flash("You don't have permission for this action", "danger")
        return redirect("/login")
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")
    
    return render_template("edit_feedback.html", form=form, feedback=feedback)

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session["username"]:
        flash("You don't have permission for this action", "danger")
        return redirect("/login")
    
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/{feedback.username}")