from App.models import User
from App.models import Admin
from App.models import Student
from App.models import Competition

from App.database import db
from flask_jwt_extended import create_access_token

"""
def create_Admin(username, password,staff_id):
    newA = Admin(username=username, password=password,staff_id=staff_id)
    db.session.add(newA)
    db.session.commit()
    return newA   

def create_Student(username, password):
    newStudent = Student(username=username, password=password)
    db.session.add(newStudent)
    db.session.commit()
    return newStudent   
"""

def get_student_by_username(username):
    return Student.query.filter_by(username=username).first()

def get_admin_by_username(username):
    return Admin.query.filter_by(username=username).first()

def get_student(id):
    return Student.query.get(id)

def get_Admin(id):
    return Admin.query.get(id)

def get_all_students():
    return Student.query.all()

def get_all_admins():
    return Admin.query.all()

def get_all_students_json():
    students = Student.query.all()
    if not students:
        return []
    students = [Student.get_json() for Student in students]
    return students

def get_all_admins_json():
    admins = Admin.query.all()
    if not admins:
        return []
    admins = [Admin.get_json() for Admin in admins]
    return admins

def get_all_competitions():
    comps=Competition.query.all()
    if not comps:
        return "No competitions found"
    else:
        comp=[Competition.get_json() for Competition in comps]
        return comp

def update_student(id, username):
    Student = get_student(id)
    if Student:
        Student.username = username
        db.session.add(Student)
        return db.session.commit()
    return None

def update_Admin(id, username):
    Admin = get_Admin(id)
    if Admin:
        Admin.username = username
        db.session.add(Admin)
        return db.session.commit()
    return None


def initialize():
    db.drop_all()
    db.create_all()
    rob = create_Admin('rob', 'robpass', 301)
    sally = create_Student('sally', 'sallypass')
    bob = create_Student('bob', 'bobpass')
    RunTime = create_Competition('SuperSprint',301)
    print( 'database intialized' )

#def add_Competition(name: str):
 #       new_Competition = Competition(name=name)
  #      db.session.add(new_Competition)
   #     db.session.commit()
    #    return new_Competition



#//write a function to create a competition



#//write a function to add a competition to a student


########################################
