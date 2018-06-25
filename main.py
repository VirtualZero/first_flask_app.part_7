from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, email

app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask_app_user:EnterYourPassword@localhost:3306/first_flask_app'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'shhhh...iAmASecret'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(75))
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, email, username, password, is_admin):
        self.email = email
        self.username = username
        self.password = password
        self.is_admin = is_admin

class Login_Form(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), email('Please enter a valid email address.')])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/')
def home():
    return render_template('home.html', title='Home')

@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = Login_Form()

    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Invalid Email', 'danger')
            return redirect('/login')

        if user and user.password != password:
            flash('Invalid Password', 'danger')
            return redirect('login')

        if user and user.password == password:
            session['email'] = email
            session['is_admin'] = user.is_admin
            flash_msg = 'Welcome, ' + user.username.title() + '!'
            flash(flash_msg, 'success')
            return redirect('/')

    return render_template('login.html', title='Login', login_form=login_form)

@app.route('/logout')
def logout():

    try:
        del session['email']
        del session['is_admin']
        flash('You have been logged out', 'warning')
        return redirect('/login')

    except KeyError:
        flash("You are not logged in.", "warning")
        return redirect('/login')

@app.before_request
def require_login():

    allowed_routes = ['login']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

if __name__ == '__main__':
    app.run()