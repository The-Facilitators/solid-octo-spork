from App.models import User, Student, Competition, Participation,Admin
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

#def sort_rankings(student):
#    return student.points

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

def display_student_info(username):
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

def register_student(username, competition_name):
  student = get_student_by_username(username)
  if student:
    competition = Competition.query.filter_by(name=competition_name).first()
    if competition:
      return student.participate_in_competition(competition)
    else:
      print(f'{competition_name} was not found')
      return None
  else:
    print(f'{username} was not found')
    return None

def notify_student(username):
  student = get_student_by_username(username)
  
  if student:
    if student.ranking != student.previous_ranking:
      student.previous_ranking = student.ranking
      db.session.add(student)
      db.session.commit()
      print(f'{student.username} has changed rankings to Rank {student.ranking}')
      return True
    else:
      print(f'{student.username} has not changed rankings')
      return False
  else:
    print(f'{username} was not found')
    return None

### Same creator ID issue, same change made. It worked 

def add_results(admin_username, student_username, competition_name, score):
  comp = Competition.query.filter_by(name=competition_name).first()
  admin = Admin.query.filter_by(username=admin_username).first()
  
  if not admin:
    print(f'{admin_username} is not an admin')
    return None
  
  if not comp:
    print(f'{competition_name} is not a valid competition')
    return None
  
  if comp.creator_id == admin.username:
    student = Student.query.filter_by(username=student_username).first()

    if not student:
      print(f'{student_username} is not a valid username')
      return None

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
        print("Score added!")
        return True

    print(f'{student_username} did not participate in {competition_name}')
    return False
  else:
    print(f'{admin_username} does not have access to add results for {competition_name}')
    return False

def display_rankings():
  students = get_all_students_json()
  if not students:
    print("No students found!")
    return None
  else:
    rankings = []
    count = 1
    students.sort(key=sort_rankings,reverse=True)
    curr_high = students[0]["total points"]
    curr_rank = 1
    for student in students:
      if curr_high != student["total points"]:
        curr_rank = count
        curr_high = student["total points"]

      stud = get_student(student["id"])
      stud.set_previous_ranking(curr_rank)
      db.session.add(stud)
      db.session.commit()
      rankings.append({"rank": curr_rank, "student": stud.username, "points": stud.points})
      count += 1
    return rankings
