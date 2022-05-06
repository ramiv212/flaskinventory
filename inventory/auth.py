from flask import Blueprint,render_template,redirect,url_for

authorize = Blueprint('auth', __name__)

@authorize.route('/login')
def login():
    return render_template('login.html')


@authorize.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    return redirect(url_for('authorize.profile'))


@authorize.route('/logout')
def logout():
    return 'Logout'


@authorize.route('/profile')
def profile():
    return render_template('profile.html')