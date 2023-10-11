from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import current_user, login_required

from.index import index_views

from App.controllers import *

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/r', methods=['GET'])
def r():
    return ('users')


@user_views.route('/users', methods=['GET'])
def get_user_page():
    students = get_all_students()
    return render_template('users.html', students=students)


"""@user_views.route('/api/competitions', methods=['GET'])
def get_competition_endpoint():
    competitions = get_all_competitions()
    if competitions:
      comp = [competition.to_dict() for competition in competitions]
      return jsonify(comp)
    else:
      return jsonify({"message": "No competitions found!"})"""

"""
@user_views.route('/api/competitions', methods=['GET'])
def get_competition_endpoint():
    competitions = get_all_competitions()
    if competitions:
        comp = [competition.to_dict() for competition in competitions]  # Use a lowercase variable name
        return jsonify(comp)  # Return the 'comp' variable, not 'competitions'
    else:
        return jsonify({"message": "No competitions found!"})"""


@user_views.route('/api/competitions', methods=['GET'])
def get_competition_endpoint():
    competitions = get_all_competitions()
    if competitions:
        return jsonify(competitions)  # Return the list of dictionaries as is
    else:
        return jsonify({"message": "No competitions found!"})



#### route to see a competition and its participants and other details
@user_views.route('/api/competitions/<int:id>', methods=['GET'])
def get_competition_by_id_endpoint(id):
    competition = get_competition(id)
    if competition:
        return jsonify(competition.to_dict()) 
    else:
        return jsonify({"error": "Competition not found"})


@user_views.route('/participate', methods=['POST'])
def participate():
    data = request.json
    username = data.get('username')
    competition_name = data.get('competition_name')

    if not username or not competition_name:
        return jsonify({"error": "Missing username or competition_name"}), 400

    student = Student.query.filter_by(username=username).first()
    competition = Competition.query.filter_by(name=competition_name).first()

    if not student:
        return jsonify({"error": f"Student with username {username} not found"}), 404

    if not competition:
        return jsonify({"error": f"Competition {competition_name} not found"}), 404

    participation = student.participate_in_competition(competition)

    if participation:
        return jsonify({"message": f"{username} registered for {competition_name}"})
    else:
        return jsonify({"error": f"{username} is already registered for {competition_name}"})


## route to see a student's details/ profile
@user_views.route('/api/details/<username>', methods=['GET'])
def get_user_details_endpoint(username):
  user_info = display_user_info(username)
  if user_info is None:
    return jsonify({"error": f"{username} is not a valid student username"})
  return jsonify(user_info)

@user_views.route('/api/users', methods=['GET'])
def get_user_page1(): 
  students = Student.query.all() 
  if not students: 
    return [] 
  students = [Student.get_json() for Student in students] 
  return jsonify(students) 


@user_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.json
    student  = create_Student(data['username'], data['password'])
    if student is None:
      return jsonify({'message': f"user {data['username']} already exists"}), 409
    return jsonify({'message': f"user {student.username} created"})

@user_views.route('/users', methods=['POST'])
def create_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_Student(data['username'], data['password'])
    return redirect(url_for('user_views.get_user_page'))

@user_views.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')

@user_views.route('/static/users', methods=['POST'])

@user_views.route('/create_competition', methods=['POST'])
def create_competition():
    data = request.json
    admin=get_Admin(data['CreatorId'])
    if admin:
      comp=get_Competition(data['name'])
      if comp is None:
        comp=create_Competition(data['name'], data['CreatorId'])
        return jsonify({'message': f"Competition {comp.name} created"})
      return jsonify({'message': f"Competition {comp.name} already exists"}), 409
    return jsonify({'message': f"Admin {data['CreatorId']} does not exist! Stop the shenanigans students"}), 409

@user_views.route('/login', methods=['POST'])
def user_login_view():
  data = request.json
  token = user_login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  return jsonify(access_token=token)

@user_views.route('/identify')
@jwt_required()
def identify_view():
  username = get_jwt_identity() # convert sent token to user name
  #retrieve regular user with given username
  user = RegularUser.query.filter_by(username=username).first()
  if user:
    return jsonify(user.get_json()) #jsonify user object
  #retrieve admin user with given username
  admin = Admin.query.filter_by(username=username).first()
  if admin:
    return jsonify(admin.get_json())#jsonify admin object

### route to add points to a student
@user_views.route('/api/addResults', methods=['POST'])
def add_results():

  data = request.json
  admin_username = data.get('admin_username')  # Ensure the key exists in the JSON data
  student_username = data.get('student_username')
  competition_name = data.get('competition_name')
  score = data.get('score')

  comp = Competition.query.filter_by(name=data['competition_name']).first()
  admin = Admin.query.filter_by(username=data['admin_username']).first()

  if not admin:
    return jsonify({"error": f'{admin_username} is not an admin'})
      
  if not comp:
    return jsonify({"error": f'{competition_name} is not a valid competition'})
    
  if comp.creator_id == admin.staff_id:
    student = Student.query.filter_by(username=data['student_username']).first()

    if not student:
      return jsonify({"error": f'{student_username} is not a valid username'})

    for participant in comp.participants:
      if participant.username == student.username:
        participation = Participation.query.filter_by(user_id=student.id, competition_id=comp.id).first()
        participation.update_points(score)
        participation.points_earned = score
        db.session.add(participation)
        db.session.commit()
        score = get_points(student.id)
        student.set_points(score)
        db.session.add(student)
        db.session.commit()
        update_rankings()
        notify_ranking_change(student)

        return jsonify({"message": "Score added!"})
        
    return jsonify({"error": f'{student_username} did not participate in {competition_name}'})
    
  return jsonify({"error": f'{admin_username} does not have access to add results for {competition_name}'})








### View rankings
@user_views.route('/api/rankings', methods=['GET'])
def display_rankings():
  students = get_all_students()

  if students:
    students.sort(key=sort_rankings, reverse=True)
    curr_high = students[0].points
    curr_rank = 1
    count = 1
    for student in students:
      if curr_high != student.points:
        curr_rank = count
        curr_high = student.points
      stud = get_student(student.id)
      stud.set_ranking(curr_rank)
      db.session.add(stud)
      db.session.commit()
      count += 1

    return jsonify({"rankings": [student.get_json() for student in students]})
  else:
    return jsonify({"message": "No students found!"})


@user_views.route('/api/register', methods=['POST'])
def register_student_for_competition():
  data = request.json
  username = data['username']
  competition_name = data['competition_name']

  if not username or not competition_name:
    return jsonify({"message": "Missing data"}), 400

  student = Student.query.filter_by(username=username).first()
  if student:
    competition = Competition.query.filter_by(name=competition_name).first()
    if competition:
      student.participate_in_competition(competition)
      return jsonify({"message": f'{username} registered for {competition_name}'})
    else:
      return jsonify({"message": f'{competition_name} was not found'}), 404
  else:
    return jsonify({"message": f'{username} was not found'}), 404



""""

   if not students:
        return jsonify({"message": "No students found!"})
    else:
        rankings = []
        count = 1
        students.sort(key=sort_rankings, reverse=True)
        curr_high = students[0]["total points"]
        curr_rank = 1
        for student in students:
            if curr_high != student["total points"]:
                curr_rank = count
                curr_high = student["total points"]

            stud = get_student(student["id"])
            stud.set_ranking(curr_rank)
            stud.set_previous_ranking(curr_rank)
            db.session.add(stud)
            db.session.commit()
            rankings.append({
                "Rank": curr_rank,
                "Student": stud.username,
                "Points": stud.points
            })
            count += 1

        return jsonify({"rankings": rankings})

      """


