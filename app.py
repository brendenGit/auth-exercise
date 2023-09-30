from flask import Flask, render_template, request, redirect, session
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_db"
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'sage123'

connect_db(app)
app.app_context().push()

@app.route("/")
def redirect_reg():
    """base route will redirect to register route"""

    return redirect("/register")

@app.route("/register", methods=['GET','POST'])
def register():
    """user registration page"""
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username=username,
                                    pwd=password,
                                    email=email,
                                    first_name=first_name,
                                    last_name=last_name)

        db.session.add(new_user)
        db.session.commit()
        session["username"] = new_user.username
        return redirect(f"/users/{new_user.username}")
    
    else:
        return render_template("register.html", form=form)


@app.route("/users/<username>")
def show_user_info(username):
    """route to show to user information - only shows if logged in"""

    if "username" in session:
        user = User.query.get_or_404(username)
        return render_template("user_info.html", user=user)
    else:
        return redirect("/login")


@app.route("/login", methods=['GET','POST'])
def login():
    """route for users to login"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        valid_user = User.authenticate(username, password)
        if valid_user:
            session["username"] = valid_user.username     
            return redirect(f"/users/{valid_user.username}")
    else:
        return render_template("login.html", form=form)


@app.route("/logout", methods=['GET'])
def logout():
    """route for users to logout"""

    session.pop("username")

    return redirect("/login")


@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    """route to delete a user - can only delete user of signed in user"""

    if session["username"] == username:
        delete_user = User.query.get_or_404(username)
        db.session.delete(delete_user)
        db.session.commit()
        return redirect("/")
    else:
        return redirect("/")


@app.route("/users/<username>/feedback/add", methods=['GET','POST'])
def add_feedback(username):
    """route for a user to create feedback"""

    if session["username"] == username:
            
            form = FeedbackForm()
            
            if form.validate_on_submit():
                title = form.title.data
                content = form.content.data

                feedback = Feedback(title=title, content=content, username=username)
                db.session.add(feedback)
                db.session.commit()
                return redirect(f"/users/{username}")
            else:
                return render_template("add_feedback.html", form=form)
    else:
        return redirect("/")