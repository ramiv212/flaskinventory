from flask import Blueprint,render_template,redirect,url_for,request,flash
from flask_login import login_user,logout_user,login_required
from inventory.models import User
from inventory import db
from werkzeug.security import generate_password_hash, check_password_hash


authorize = Blueprint('authorize', __name__)

@authorize.route('/')
def login():

	# user = User.query.filter_by(email='ramiro@clearavl.com').first()
	# setattr(user, "password", generate_password_hash("noneya!12"))
	# db.session.commit()

	return render_template('login.html')


@authorize.route('/login', methods=['POST'])
def login_post():

	# login code goes here
	email = request.form.get('email')
	password = request.form.get('password')
	remember = True if request.form.get('remember') else False

	user = User.query.filter_by(email=email).first()

	print(user)

	# check if the user actually exists
	# take the user-supplied password, hash it, and compare it to the hashed password in the database
	if not user or not check_password_hash(user.password, password):
		flash('Please check your login details and try again.')
		print('Please check your login details and try again.')
		return redirect(url_for('authorize.login')) # if the user doesn't exist or password is wrong, reload the page

	# if the above check passes, then we know the user has the right credentials
	login_user(user, remember=remember)

	flash(f'Welcome, {user.name}!')

	return redirect(url_for('homepage.home_page'))


@authorize.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('authorize.logout'))
