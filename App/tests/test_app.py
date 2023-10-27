import csv
import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash
from App.controllers.student import register_student

from App.main import create_app
from App.database import db, create_db
from App.models import *
from App.controllers import *
from wsgi import initialize


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UnitTests(unittest.TestCase):

    #Student Unit Test
    def test_new_student(self):
      db.drop_all()
      db.create_all()
      student = Student("bob", "bobpass")
      assert student.username == "bob"

    def test_set_points(self):
      db.drop_all()
      db.create_all()
      student = Student("bob", "bobpass")
      student.set_points(15)
      assert student.points == 15

    def test_set_ranking(self):
      db.drop_all()
      db.create_all()
      student = Student("bob", "bobpass")
      student.set_ranking(2)
      assert student.ranking == 2

    def test_previous_ranking(self):
      db.drop_all()
      db.create_all()
      student = Student("bob", "bobpass")
      student.set_previous_ranking(3)
      assert student.previous_ranking == 3

    def test_student_get_json(self):
      db.drop_all()
      db.create_all()
      student = Student("bob", "bobpass")
      self.assertDictEqual(student.get_json(), {"id": None, "username":"bob", "role": 'Student', "total points": None, "overall rank": None})
  
    #Admin Unit Test
    def test_new_admin(self):
      db.drop_all()
      db.create_all()
      admin = Admin("rob", "robpass", 1001)
      assert admin.username == "rob" and admin.staff_id == 1001

    def test_admin_get_json(self):
      db.drop_all()
      db.create_all()
      admin = Admin("rob", "robpass", 1001)
      self.assertDictEqual(admin.get_json(), {"id":None, "username":"rob", "role": 'Admin', "staff_id": 1001})
  
    #Competition Unit Test
    def test_new_competition(self):
      db.drop_all()
      db.create_all()
      competition = Competition("RunTime", 1)
      assert competition.name == "RunTime"

    def test_competition_get_json(self):
      db.drop_all()
      db.create_all()
      competition = Competition("RunTime", 1)
      self.assertDictEqual(competition.get_json(), {"id": None,"name": "RunTime", "creator_id": 1, "participants": []})

    #Participation Unit Test
    def test_new_participation(self):
      db.drop_all()
      db.create_all()
      participation = Participation(1, 2)
      assert participation.user_id == 1 and participation.competition_id == 2

    def test_update_points(self):
      db.drop_all()
      db.create_all()
      participation = Participation(1, 2)
      participation.update_points(15)
      assert participation.points_earned == 15
    
    def test_participation_get_json(self):
      db.drop_all()
      db.create_all()
      participation = Participation(1, 2)
      self.assertDictEqual(participation.get_json(), {"id": None, "user_id": 1, "competition_id": 2, "points_earned": None})

    #User Unit Test
    def test_new_user(self):
      db.drop_all()
      db.create_all()
      user = User("bob", "bobpass")
      assert user.username == "bob"
  
    def test_hashed_password(self):
      db.drop_all()
      db.create_all()
      user = User("bob", "bobpass")
      assert user.password != "bobpass"

    def test_check_password(self):
      db.drop_all()
      db.create_all()
      user = User("bob", "bobpass")
      assert user.check_password("bobpass")

'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()

class IntegrationTests(unittest.TestCase):
    def test_create_student(self):
      db.drop_all()
      db.create_all()
      student = create_Student("bob", "bobpass")
      assert student.username == "bob"

    def test_create_admin(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("rob", "robpass", 1001)
      assert admin.username == "rob"
  
    def test1_login_student(self):
      db.drop_all()
      db.create_all()
      student = create_Student("bob", "bobpass")
      assert login_student("bob", "bobpass") == True
      
    def test2_login_student(self):
      db.drop_all()
      db.create_all()
      student = create_Student("bob", "bobpass")
      assert login_student("bob", "bobpassword") == False
  
    def test1_login_admin(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("rob", "robpass", 1001)
      assert login_admin("rob", "robpass", 1001) == True

    def test2_login_admin(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("rob", "robpass", 1001)
      assert login_admin("rob", "robpass", 1010) == False
      
    def test1_create_competition(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("rob", "robpass", 1001)
      comp = create_Competition("RunTime", 1001)
      assert comp.name == "RunTime"

    def test2_create_competition(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("rob", "robpass", 1001)
      assert create_Competition("CodeSprint", 10) is None

    def test_student_list(self):
      db.drop_all()
      db.create_all()
      kim = create_Admin('kim', 'kimpass', 1000)
      rob = create_Admin('rob', 'robpass', 1001)
      ben = create_Student('ben', 'benpass')
      sally = create_Student('sally', 'sallypass')
      bob = create_Student('bob', 'bobpass')
      jake = create_Student('jake', 'jakepass')
      amy = create_Student('amy', 'amypass')
      comp1 = create_Competition('CodeSprint', 1000)
      comp2 = create_Competition('RunTime', 1001)
      comp3 = create_Competition('HashCode', 1001)

      with open('registration.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            register_student(row['username'], row['competition_name'])

      with open('scores.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
          add_results(row['admin'], row['student'], row['comp'], row['score'])

      students = get_all_students_json()
      self.assertEqual(students, [{'id': 1, 'username': 'ben', 'role': 'Student', 'total points': 25, 'overall rank': 1}, {'id': 2, 'username': 'sally', 'role': 'Student', 'total points': 20, 'overall rank': 2}, {'id': 3, 'username': 'bob', 'role': 'Student', 'total points': 15, 'overall rank': 4}, {'id': 4, 'username': 'jake', 'role': 'Student', 'total points': 10, 'overall rank': 5}, {'id': 5, 'username': 'amy', 'role': 'Student', 'total points': 20, 'overall rank': 2}])

    def test_admin_list(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("kim", "kimpass", 1000)
      admin = create_Admin("rob", "robpass", 1001)
      admins = get_all_admins_json()
      self.assertEqual(admins, [{'id': 1, 'username': 'kim', 'role': 'Admin', "staff_id": 1000}, {'id': 2, 'username': 'rob', 'role': 'Admin', "staff_id": 1001}])

## Same Creator ID issue

    def test_comp_list(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("kim", "kimpass", 1000)
      admin = create_Admin("rob", "robpass", 1001)
      comp1 = create_Competition("CodeSprint", 1000)
      comp2 = create_Competition("RunTime", 1001)
      comp3 = create_Competition("HashCode", 1001)
      comps = print_all_competitions()
      
      self.assertListEqual(comps, [{"id":1, "name":"CodeSprint", "creator_id": 1000, "participants": []}, {"id":2, "name":"RunTime", "creator_id": 1001, "participants": []}, {"id":3, "name":"HashCode", "creator_id": 1001, "participants": []}])

    def test_participation_list(self):
      db.drop_all()
      db.create_all()
      kim = create_Admin('kim', 'kimpass', 1000)
      rob = create_Admin('rob', 'robpass', 1001)
      ben = create_Student('ben', 'benpass')
      sally = create_Student('sally', 'sallypass')
      bob = create_Student('bob', 'bobpass')
      jake = create_Student('jake', 'jakepass')
      amy = create_Student('amy', 'amypass')
      comp1 = create_Competition('CodeSprint', 1000)
      comp2 = create_Competition('RunTime', 1001)
      comp3 = create_Competition('HashCode', 1001)

      with open('registration.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            register_student(row['username'], row['competition_name'])

      with open('scores.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
          add_results(row['admin'], row['student'], row['comp'], row['score'])

      participations = print_all_participations()
      self.assertListEqual(participations, [{'id': 1, 'user_id': 1, 'competition_id': 1, 'points_earned': 10}, {'id': 2, 'user_id': 1, 'competition_id': 2, 'points_earned': 10}, {'id': 3, 'user_id': 1, 'competition_id': 3, 'points_earned': 5}, {'id': 4, 'user_id': 2, 'competition_id': 1, 'points_earned': 10}, {'id': 5, 'user_id': 2, 'competition_id': 3, 'points_earned': 10}, {'id': 6, 'user_id': 3, 'competition_id': 2, 'points_earned': 15}, {'id': 7, 'user_id': 3, 'competition_id': 3, 'points_earned': 0}, {'id': 8, 'user_id': 4, 'competition_id': 2, 'points_earned': 10}, {'id': 9, 'user_id': 5, 'competition_id': 1, 'points_earned': 20}])
  
    def test1_register_student(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("rob", "robpass", 1001)
      student = create_Student("bob", "bobpass")
      comp = create_Competition("RunTime", 1001)
      assert register_student("bob", "RunTime") != None


## The test passed but I don't undertand it 
    def test2_register_student(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("rob", "robpass", 1001)
      student = create_Student("bob", "bobpass")
      comp = create_Competition("RunTime", 1001)
      register_student("bob", "RunTime")
      assert register_student("bob", "RunTime") == None

    def test1_add_results(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("rob", "robpass", 1001)
      student = create_Student("bob", "bobpass")
      comp = create_Competition("RunTime", 1001)
      register_student("bob", "RunTime")
      assert add_results("rob", "bob", "RunTime", 15) == True

    def test2_add_results(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("rob", "robpass", 1001)
      student = create_Student("bob", "bobpass")
      comp = create_Competition("RunTime", 1001)
      assert add_results("rob", "bob", "RunTime", 15) == False

    def test3_add_results(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("kim", "kimpass", 1000)
      admin1 = create_Admin("rob", "robpass", 1001)
      student = create_Student("bob", "bobpass")
      comp = create_Competition("RunTime", 1001)
      register_student("bob", "RunTime")
      assert add_results("kim", "bob", "RunTime", 15) == False
  
    def test_display_student_info(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("rob", "robpass", 1001)
      student = create_Student("bob", "bobpass")
      comp = create_Competition("RunTime", 1001)
      register_student("bob", "RunTime")
      add_results("rob", "bob", "RunTime", 15)
      self.assertDictEqual(display_student_info("bob"), {"profile": {'id': 1, 'username': 'bob', 'role': 'Student', 'total points': 15, 'overall rank': 1}, "participated_competitions": ['RunTime']})

    def test_display_admin_info(self):
      db.drop_all()
      db.create_all()
      admin = create_Admin("kim", "kimpass", 1000)
      admin1 = create_Admin("rob", "robpass", 1001)
      comp1 = create_Competition('CodeSprint', 1000)
      comp2 = create_Competition('RunTime', 1001)
      comp3 = create_Competition('HashCode', 1001)
      self.assertDictEqual(display_admin_info("rob"), {"profile":{'id': 2, 'username': 'rob', 'role': 'Admin', 'staff_id': 1001}, "competitions created": ["RunTime", "HashCode"]})
  
  ## Same thing
    def test_competition_details(self):
      db.drop_all()
      db.create_all()
      kim = create_Admin('kim', 'kimpass', 1000)
      rob = create_Admin('rob', 'robpass', 1001)
      ben = create_Student('ben', 'benpass')
      sally = create_Student('sally', 'sallypass')
      bob = create_Student('bob', 'bobpass')
      jake = create_Student('jake', 'jakepass')
      amy = create_Student('amy', 'amypass')
      comp1 = create_Competition('CodeSprint', 1000)
      comp2 = create_Competition('RunTime', 1001)
      comp3 = create_Competition('HashCode', 1001)

      with open('registration.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
           register_student(row['username'], row['competition_name'])

      with open('scores.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
          add_results(row['admin'], row['student'], row['comp'], row['score'])
      
      self.assertListEqual(display_competition_details(), [[{'id': 1, 'name': 'CodeSprint', "creator_id": 1000, "participants": ["ben", "sally", "amy"]}, [{'id': 1, 'user_id': 1, 'competition_id': 1, 'points_earned': 10}, {'id': 4, 'user_id': 2, 'competition_id': 1, 'points_earned': 10}, {'id': 9, 'user_id': 5, 'competition_id': 1, 'points_earned': 20}]], [{'id': 2, 'name': 'RunTime', "creator_id": 1001, "participants": ["ben", "bob", "jake"]}, [{'id': 2, 'user_id': 1, 'competition_id': 2, 'points_earned': 10}, {'id': 6, 'user_id': 3, 'competition_id': 2, 'points_earned': 15}, {'id': 8, 'user_id': 4, 'competition_id': 2, 'points_earned': 10}]], [{'id': 3, 'name': 'HashCode', "creator_id": 1001, "participants": ["ben", "sally", "bob"]}, [{'id': 3, 'user_id': 1, 'competition_id': 3, 'points_earned': 5}, {'id': 5, 'user_id': 2, 'competition_id': 3, 'points_earned': 10}, {'id': 7, 'user_id': 3, 'competition_id': 3, 'points_earned': 0}]]])

    def test_display_rankings(self):
      db.drop_all()
      db.create_all()
      kim = create_Admin('kim', 'kimpass', 1000)
      rob = create_Admin('rob', 'robpass', 1001)
      ben = create_Student('ben', 'benpass')
      sally = create_Student('sally', 'sallypass')
      bob = create_Student('bob', 'bobpass')
      jake = create_Student('jake', 'jakepass')
      amy = create_Student('amy', 'amypass')
      comp1 = create_Competition('CodeSprint', 1000)
      comp2 = create_Competition('RunTime', 1001)
      comp3 = create_Competition('HashCode', 1001)

      with open('registration.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
           register_student(row['username'], row['competition_name'])

      with open('scores.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
          add_results(row['admin'], row['student'], row['comp'], row['score'])
      
      self.assertEqual(display_rankings(), [{"rank": 1, "student": "ben", "points": 25}, {"rank": 2, "student": "sally", "points": 20}, {"rank": 2, "student": "amy", "points": 20}, {"rank": 4, "student": "bob", "points": 15}, {"rank": 5, "student": "jake", "points": 10},])

    def test1_notify_student(self):
      db.drop_all()
      db.create_all()
      kim = create_Admin('kim', 'kimpass', 1000)
      rob = create_Admin('rob', 'robpass', 1001)
      ben = create_Student('ben', 'benpass')
      sally = create_Student('sally', 'sallypass')
      bob = create_Student('bob', 'bobpass')
      jake = create_Student('jake', 'jakepass')
      amy = create_Student('amy', 'amypass')
      comp1 = create_Competition('CodeSprint', 1000)
      comp2 = create_Competition('RunTime', 1001)
      comp3 = create_Competition('HashCode', 1001)

      with open('registration.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
           register_student(row['username'], row['competition_name'])

      with open('scores.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
          add_results(row['admin'], row['student'], row['comp'], row['score'])

      add_results("rob", "bob", "HashCode", 15)
      assert notify_student("bob") == True

    def test2_notify_student(self):
      db.drop_all()
      db.create_all()
      kim = create_Admin('kim', 'kimpass', 1000)
      rob = create_Admin('rob', 'robpass', 1001)
      ben = create_Student('ben', 'benpass')
      sally = create_Student('sally', 'sallypass')
      bob = create_Student('bob', 'bobpass')
      jake = create_Student('jake', 'jakepass')
      amy = create_Student('amy', 'amypass')
      comp1 = create_Competition('CodeSprint', 1000)
      comp2 = create_Competition('RunTime', 1001)
      comp3 = create_Competition('HashCode', 1001)

      with open('registration.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
           register_student(row['username'], row['competition_name'])

      with open('scores.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
          add_results(row['admin'], row['student'], row['comp'], row['score'])

      display_student_info("bob")
      assert notify_student("bob") == False
