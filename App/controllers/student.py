from App.models import User, Student, Competition, Participation
#from App.controllers import competition

from App.database import db
from flask_jwt_extended import create_access_token

def create_Student(username, password):
    Here = Student.query.filter_by(username=username).first()
    if Here:
        print(f'{username} already exists!')
        return None
    newStudent = Student(username=username, password=password)
    try:
      db.session.add(newStudent)
      db.session.commit()
      print(f'New Student: {username} created!')
    except Exception as e:
      db.session.rollback()
      print(f'Something went wrong creating {username}')
    return newStudent


def get_student_by_username(username):
    return Student.query.filter_by(username=username).first()

def get_student(id):
    return Student.query.get(id)

def get_competition(id):
  return Competition.query.get(id)

def get_points(id):
    student = get_student(id)
    score = 0
    for comp in student.competitions: 
      participation = Participation.query.filter_by(user_id=id, competition_id=comp.id).first()
      if participation:
        score += participation.points_earned
    return score

def get_ranking(id):
    student = get_student(id)
    return student.ranking

def sort_rankings(value):
  return value["total points"]

def update_rankings():
  students = get_all_students_json()
  count = 1
  if students:
    students.sort(key=sort_rankings,reverse=True)
    curr_high = students[0]["total points"]
    curr_rank = 1
    for student in students:
      if curr_high != student["total points"]:
        curr_rank = count
        curr_high = student["total points"]
      
      stud = get_student(student["id"])
      stud.set_ranking(curr_rank)
      db.session.add(stud)
      db.session.commit()
      count += 1

def get_all_students():
    return Student.query.all()

def get_all_students_json():
    students = Student.query.all()
    if not students:
        return []
    students = [Student.get_json() for Student in students]
    return students

def update_student(id, username):
    Student = get_student(id)
    if Student:
        Student.username = username
        db.session.add(Student)
        return db.session.commit()
    return None

"""def display_user_info(username):
  student = Student.query.filter_by(username=username).first()
  
  if not student:
    print(f'{username} is not a valid student username')
    return None
  else:
    score = get_points(student.id)
    student.set_points(score)
    print("Profile Infomation")
    print(student.get_json())
    print("Participated in the following competitions:")
    for comp in student.competitions:
      print(f'{comp.name} ')"""

def display_user_info(username):
    student = Student.query.filter_by(username=username).first()

    if not student:
        return None
    else:
        score = get_points(student.id)
        student.set_points(score)
        profile_info = {
            "profile": student.get_json(),
            "participated_competitions": [comp.name for comp in student.competitions]
        }
        return profile_info