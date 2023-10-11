from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import login_required, login_user, current_user, logout_user

from.index import index_views

from App.controllers import *
from App.models import *


auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''

@auth_views.route('/users', methods=['GET'])
def get_user_page():
    students = get_all_students()
    return render_template('users.html', students=students)


@auth_views.route('/identify', methods=['GET'])
@login_required
def identify_page():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/login', methods=['POST'])
def login_action():
    username = request.form.get('username')
    password = request.form.get('password')
    user = None
    if Admin.query.filter_by(username=username).first():
        user = login_Admin(username, password)
    elif Student.query.filter_by(username=username).first():
        user = login_Student(username, password)
    if user:
        return redirect('/')
    flash('Invalid username/password')
    return redirect('/login')


'''
@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    user = login(data['username'], data['password'])
    if user:
        login_user(user)
        return 'user logged in!'
    return 'bad username or password given', 401
'''
@auth_views.route('/logout', methods=['GET'])
def logout_action():
    data = request.form
    user = login(data['username'], data['password'])
    return 'logged out!'

'''
API Routes
'''

@auth_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@auth_views.route('/api/admin', methods=['GET'])
def get_Admin():
    admins = get_all_admins_json()
    return jsonify(admins)

@auth_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.json
    create_user(data['username'], data['password'])
    return jsonify({'message': f"user {data['username']} created"})
    
#####create _Admin changed to create_user

@auth_views.route('/api/admin', methods=['POST'])
def create_admin():
    data = request.json
    admin = create_Admin(data['username'], data['password'], data['staff_id'])
    if admin:
        return jsonify({'message': f"admin {admin.username} created"})
    else:
        return jsonify({'message': f"Failed to create admin"})


@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = jwt_authenticate(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  return jsonify(access_token=token)

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user_action():
    return jsonify({'message': f"username: {jwt_current_user.username}, id : {jwt_current_user.id}"})



############################################################################
'''
@auth_views.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@auth_views.route('/login', methods=['POST'])
def login_action():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    user = None
    if role == 'customer':
        user = login_customer(username, password)
    elif role == 'staff':
        user = login_staff(username, password)
    if user:
        return redirect('/')
    flash('Invalid username/password')
    return redirect('/login')

@auth_views.route('/login', methods=['POST'])
def login_action():
    username = request.form.get('username')
    password = request.form.get('password')
    user = None
    if Admin.query.filter_by(username=username).first():
        user = login_Admin(username, password)
    elif Student.query.filter_by(username=username).first():
        user = login_Student(username, password)
    if user:
        return redirect('/')
    flash('Invalid username/password')
    return redirect('/login')



@auth_views.route('/logout', methods=['GET'])
def logout_action():
    logout_user()
    return redirect('/')

    '''