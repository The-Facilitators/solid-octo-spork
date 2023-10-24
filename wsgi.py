import click, pytest, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.main import create_app
from App.controllers import *

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    db.drop_all()
    db.create_all()
    create_Admin('Kim', 'Possible',33)
    create_Admin('Dr', 'robpass', 991)
    create_Student('sally', 'sallypass')
    create_Student('robin', 'Hood')
    create_Competition('RunTime',33)
    create_Competition('SuperSprint',991)

    print('database intialized')

@app.cli.command("login", help="Login")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def login_user_command(username, password):
    access_token = jwt_authenticate(username, password)
    if access_token:
        student = Student.query.filter_by(username=username).first()
        admin = Admin.query.filter_by(username=username).first()
        if student:
            print(f'Student logged in!\nUser: {student}\nAccess Token: {access_token}')
        elif admin:
            print(f'Admin logged in!\nUser: {admin}\nAccess Token: {access_token}')
    else:
        print('Login unsuccessful!')

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
student_cli = AppGroup('student', help='Student object commands') 
 
@student_cli.command("create", help="Creates a Student")
@click.argument("username", default="James")
@click.argument("password", default="T.Kirk")
def create_student_command(username, password):
    create_Student(username, password)

## Use click.prompts

"""@student_cli.command("participate", help="Student")
@click.argument("id", default="2")
@click.argument("competition_id", default="1")
def student_Participate(id, competition_id):
    student = get_student(id)
    if student:
        competition = get_competition(competition_id)
        if competition:
            student.participate_in_competition(competition_id)
            print(f'{Student.id} is a participant in a competition!')
        else:
            print(f'Competition {competition_id} not found')
    else:
        print(f'Student {competition_id} not found')"""
        
@student_cli.command("register", help="Registers student for competitions")
@click.argument("username", default="bob")
@click.argument("competition_name", default="RunTime")
def register_student_command(username, competition_name):
    student = Student.query.filter_by(username=username).first()
    if student:
      competition = Competition.query.filter_by(name=competition_name).first()
      if competition:
        student.participate_in_competition(competition)
        #competition.add_participant(student)
      else:
        print(f'{competition_name} was not found')
    else:
      print(f'{username} was not found')

@student_cli.command("view-details", help="displays user information")
@click.argument("username", default="bob")
def display_user_info(username):
  student = Student.query.filter_by(username=username).first()
  
  if not student:
    print(f'{username} is not a valid student username')
  else:
    score = get_points(student.id)
    student.set_points(score)
    print("Profile Infomation")
    print(student.get_json())
    print("Participated in the following competitions:")
    for comp in student.competitions:
      print(f'{comp.name} ')


"""
@user_cli.command("login", help="Lists users in the database")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def login_user_command(username, password):
    access_token = jwt_authenticate(username, password)
    if access_token:
        student = Student.query.filter_by(username=username).first()
        admin = Admin.query.filter_by(username=username).first()
        if student:
            return student, access_token, f'Token: {access_token}'
        elif admin:
            return admin, access_token, f'Access Token: {access_token}'
    return None, None, 'bad username or password given', 401



@student_cli.command("login", help="Log in a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def login_user_command(username, password):
    access_token = jwt_authenticate(username, password)
    if access_token:
        student = Student.query.filter_by(username=username).first()
        admin = Admin.query.filter_by(username=username).first()
        if student:
            print(f'Student logged in!\nUser: {student}\nAccess Token: {access_token}')
        elif admin:
            print(f'Admin logged in!\nUser: {admin}\nAccess Token: {access_token}')
    else:
        print('Login unsuccessful!')


"""


# Then define the command and any parameters and annotate it with the group (@)


# this command will be : flask user create bob bobpass

@student_cli.command("list", help="Lists students in the database")
@click.argument("format", default="string")
def list_student_command(format):
    if format == 'string':
        print(get_all_students())
    else:
        print(get_all_students_json()) 

@student_cli.command("notification", help="Notify a change in standings")
@click.argument("username", default="bob")
def notify_user(username):
  student = Student.query.filter_by(username=username).first()
  if student:
    if student.ranking != student.previous_ranking:
      print(f'{student.username} has changed rankings to Rank {student.ranking}')
      student.previous_ranking = student.ranking
      db.session.add(student)
      db.session.commit()
    else:
      print(f'{student.username} has not changed rankings')
  else:
    print(f'{username} was not found')

app.cli.add_command(student_cli) # add the group to the cli

admin_cli = AppGroup('Admin', help='Admin object commands') 

@admin_cli.command("createAdmin", help="Creates an admin")
@click.argument("username", default="Dave")
@click.argument("password", default="NBuster")
@click.argument("staff_id", default="1001")
def create_admin_command(username, password, staff_id):
    create_Admin(username, password, staff_id)

@admin_cli.command("createCompetition", help="Creates a competition")
@click.argument("competition_name", default="RunTime")
@click.argument("username", default="rob")
#@jwt_required()
def create_competition_command(competition_name, username):
  #username = get_jwt_identity()
  admin = Admin.query.filter_by(username=username).first()
  if admin:
    create_Competition(competition_name, admin.id)


@admin_cli.command("list", help="Lists admins in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_admins())
    else:
        print(get_all_admins_json())


@admin_cli.command("addResults",help="enters scores of participants of the competition")
@click.argument("admin_username", default="rob")
@click.argument("student_username", default="bob")
@click.argument("competition_name", default="RunTime")
@click.argument("score", default=10)
def add_results(admin_username, student_username, competition_name, score):
  comp = Competition.query.filter_by(name=competition_name).first()
  admin = Admin.query.filter_by(username=admin_username).first()
  
  if not admin:
    print(f'{admin_username} is not an admin')
    return
  
  if not comp:
    print(f'{competition_name} is not a valid competition')
    return
  
  if comp.creator_id == admin.id:
    student = Student.query.filter_by(username=student_username).first()
    
    if not student:
      print(f'{student_username} is not a valid username')
      return
    
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
        #competition.participants = participation
        """for participant in comp.participants:
          if participant.id == participation.id:
            participant.point_earned = participation.point_earned
            db.session.add(participant)
        db.session.commit()"""
        print("Score added!")
        return
        
    print(f'{student_username} did not participate in {competition_name}')
    
  else:
    print(f'{admin_username} does not have access to add results for {competition_name}')

app.cli.add_command(admin_cli)

user_cli = AppGroup('user', help='User object commands')

@user_cli.command("comp-list", help="Lists competitions in the database")
def list_comp_command():
    print(get_all_competitions())

@user_cli.command("participation-list", help="Lists participants in the database")
def list_participation_command():
      print(get_all_participations())

@user_cli.command("competition-details", help="displays competition details")
def display_competition_details():
  comps = Competition.query.all()

  if not comps:
    print("No competitions found!")
  else:
    for comp in comps:
      print(comp.get_json())
      participants = Participation.query.filter_by(competition_id=comp.id).all()

      if not participants:
        print("No participants found!")
      else:
        for participant in participants:
          #participation = Participation.query.filter_by(user_id=participant.id).first()
          #if participation:
          print(participant.get_json())

@user_cli.command("rankings", help="displays competition ranking")
def display_ranking():
  students = get_all_students_json()

  if not students:
    print("No students found!")
  else:
    print("Rankings:")
    count = 1
    students.sort(key=sort_rankings,reverse=True)
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
      print(f'Rank: {curr_rank}\tStudent: {stud.username}\tPoints: {stud.points}')
      count += 1

app.cli.add_command(user_cli)

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)



