import csv
import click, pytest, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from flask_jwt_extended import get_jwt_identity

from App.database import db, get_migrate
from App.main import create_app
from App.controllers import *
from App.models import *

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    db.drop_all()
    db.create_all()
    kim = create_admin('kim', 'kimpass', 1000)
    rob = create_admin('rob', 'robpass', 1001)
    ben = create_student('ben', 'benpass')
    sally = create_student('sally', 'sallypass')
    bob = create_student('bob', 'bobpass')
    jake = create_student('jake', 'jakepass')
    amy = create_student('amy', 'amypass')
    comp1 = create_competition('CodeSprint', 'kim')
    comp2 = create_competition('RunTime', 'rob')
    comp3 = create_competition('HashCode', 'rob')
    with open('registration.csv') as file:
      reader = csv.DictReader(file)
      for row in reader:
         register_student(row['username'], row['competition_name'])
    with open('scores.csv') as file:
      reader = csv.DictReader(file)
      for row in reader:
        add_results(row['admin'], row['student'], row['comp'], row['score'])
      print('database initialized')

student_cli = AppGroup('student', help='Student object commands') 

@student_cli.command("login", help="Log in a student")
@click.argument("username", default="bob")
@click.argument("password", default="bobpass")
def login_student_command(username, password):
    login_student(username, password)

@student_cli.command("create-student", help="Creates a Student")
@click.argument("username", default="bob")
@click.argument("password", default="bobpass")
def create_student_command(username, password):
    create_student(username, password)

@student_cli.command("list", help="Lists students in the database")
def list_student_command():
    print(get_all_students_json()) 

@student_cli.command("register", help="Registers student for competitions")
@click.argument("username", default="bob")
@click.argument("competition_name", default="RunTime")
def register_student_command(username, competition_name):
    register_student(username, competition_name)

@student_cli.command("view-details", help="displays student information")
@click.argument("username", default="bob")
def display_student_info_command(username):
    display_student_info(username)

@student_cli.command("notification", help="Notify a change in standings")
@click.argument("username", default="bob")
def notify_student_command(username):
    notify_student(username)

app.cli.add_command(student_cli)


admin_cli = AppGroup('admin', help='Admin object commands') 

@admin_cli.command("login", help="Log in an admin")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
@click.argument("staff_id", default="1001")
def login_admin_command(username, password, staff_id):
    login_admin(username, password, staff_id)

@admin_cli.command("create-admin", help="Creates an admin")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
@click.argument("staff_id", default="1001")
def create_admin_command(username, password, staff_id):
    create_admin(username, password, staff_id)

@admin_cli.command("create-competition", help="Creates a competition")
@click.argument("competition_name", default="RunTime")
@click.argument("username", default="rob")
def create_competition_command(competition_name, username):
    create_competition(competition_name, username)

@admin_cli.command("list", help="Lists admins in the database")
def list_admins_command():
    print(get_all_admins_json())

@admin_cli.command("view-details", help="displays admin information")
@click.argument("username", default="rob")
@click.argument("staff_id", default=1001)
def display_admin_info_command(username, staff_id):
    display_admin_info(username, staff_id)

@admin_cli.command("add-results",help="enters scores of participants of the competition")
@click.argument("admin_username", default="rob")
@click.argument("student_username", default="bob")
@click.argument("competition_name", default="RunTime")
@click.argument("score", default=10)
def add_results_command(admin_username, student_username, competition_name, score):
    add_results(admin_username, student_username, competition_name, score)

app.cli.add_command(admin_cli)


user_cli = AppGroup('user', help='User object commands')

@user_cli.command("comp-list", help="Lists competitions in the database")
def list_comp_command():
    print(get_all_competitions_json())

@user_cli.command("participation-list", help="Lists participants in the database")
def list_participation_command():
    print(get_all_participations_json())

@user_cli.command("competition-details", help="displays competition details")
def display_competition_details_command():
    display_competition_details()

@user_cli.command("rankings", help="displays competition ranking")
def display_rankings_command():
    display_rankings()

app.cli.add_command(user_cli)


'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("all", help="Run All tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "IntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)



