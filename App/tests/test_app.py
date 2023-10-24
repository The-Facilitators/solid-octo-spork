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
      competition = Competition("RunTime", 1001)
      assert competition.name == "RunTime"

    def test_competition_get_json(self):
      db.drop_all()
      db.create_all()
      competition = Competition("RunTime", 1001)
      self.assertDictEqual(competition.get_json(), {"id": None,"name": "RunTime"})

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
      student = create_student("bob", "bobpass")
      assert student.username == "bob"

    def test_create_admin(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("rob", "robpass", 1001)
      assert admin.username == "rob"
  
    def test1_login_student(self):
      db.drop_all()
      db.create_all()
      student = create_student("bob", "bobpass")
      assert login_student("bob", "bobpass") == True
      
    def test2_login_student(self):
      db.drop_all()
      db.create_all()
      student = create_student("bob", "bobpass")
      assert login_student("bob", "bobpassword") == False
  
    def test1_login_admin(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("rob", "robpass", 1001)
      assert login_admin("rob", "robpass", 1001) == True

    def test2_login_admin(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("rob", "robpass", 1001)
      assert login_admin("rob", "robpass", 1010) == False
      
    def test1_create_competition(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("rob", "robpass", 1001)
      comp = create_competition("RunTime", "rob")
      assert comp.name == "RunTime"

    def test2_create_competition(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("rob", "robpass", 1001)
      assert create_competition("CodeSprint", "jim") == None

    def test_student_list(self):
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

      students = get_all_students_json()
      self.assertEqual(students, [{'id': 1, 'username': 'ben', 'role': 'Student', 'total points': 25, 'overall rank': 1}, {'id': 2, 'username': 'sally', 'role': 'Student', 'total points': 20, 'overall rank': 2}, {'id': 3, 'username': 'bob', 'role': 'Student', 'total points': 15, 'overall rank': 4}, {'id': 4, 'username': 'jake', 'role': 'Student', 'total points': 10, 'overall rank': 5}, {'id': 5, 'username': 'amy', 'role': 'Student', 'total points': 20, 'overall rank': 2}])

    def test_admin_list(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("kim", "kimpass", 1000)
      admin = create_admin("rob", "robpass", 1001)
      admins = get_all_admins_json()
      self.assertEqual(admins, [{'id': 1, 'username': 'kim', 'role': 'Admin', "staff_id": 1000}, {'id': 2, 'username': 'rob', 'role': 'Admin', "staff_id": 1001}])

    def test_comp_list(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("kim", "kimpass", 1000)
      admin = create_admin("rob", "robpass", 1001)
      comp1 = create_competition("CodeSprint", "kim")
      comp2 = create_competition("RunTime", "rob")
      comp3 = create_competition("HashCode", "rob")
      comps = get_all_competitions_json()
      self.assertListEqual(comps, [{"id":1, "name":"CodeSprint"}, {"id":2, "name":"RunTime"}, {"id":3, "name":"HashCode"}])

    def test_participation_list(self):
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

      participations = get_all_participations_json()
      self.assertListEqual(participations, [{'id': 1, 'user_id': 1, 'competition_id': 1, 'points_earned': 10}, {'id': 2, 'user_id': 1, 'competition_id': 2, 'points_earned': 10}, {'id': 3, 'user_id': 1, 'competition_id': 3, 'points_earned': 5}, {'id': 4, 'user_id': 2, 'competition_id': 1, 'points_earned': 10}, {'id': 5, 'user_id': 2, 'competition_id': 3, 'points_earned': 10}, {'id': 6, 'user_id': 3, 'competition_id': 2, 'points_earned': 15}, {'id': 7, 'user_id': 3, 'competition_id': 3, 'points_earned': 0}, {'id': 8, 'user_id': 4, 'competition_id': 2, 'points_earned': 10}, {'id': 9, 'user_id': 5, 'competition_id': 1, 'points_earned': 20}])
  
    def test1_register_student(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("rob", "robpass", 1001)
      student = create_student("bob", "bobpass")
      comp = create_competition("RunTime", "rob")
      self.assertEqual(register_student("bob", "RunTime"), "bob was registered for RunTime")

    def test2_register_student(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("rob", "robpass", 1001)
      student = create_student("bob", "bobpass")
      comp = create_competition("RunTime", "rob")
      register_student("bob", "RunTime")
      self.assertEqual(register_student("bob", "RunTime"), "bob is already registered for RunTime")

    def test1_add_results(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("rob", "robpass", 1001)
      student = create_student("bob", "bobpass")
      comp = create_competition("RunTime", "rob")
      register_student("bob", "RunTime")
      add_results("rob", "bob", "RunTime", 15)
      self.assertEqual(add_results("rob", "bob", "RunTime", 15), "Score added!")

    def test2_add_results(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("rob", "robpass", 1001)
      student = create_student("bob", "bobpass")
      comp = create_competition("RunTime", "rob")
      self.assertEqual(add_results("rob", "bob", "RunTime", 15), "bob did not participate in RunTime")

    def test3_add_results(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("kim", "kimpass", 1000)
      admin1 = create_admin("rob", "robpass", 1001)
      student = create_student("bob", "bobpass")
      comp = create_competition("RunTime", "rob")
      self.assertEqual(add_results("kim", "bob", "RunTime", 15), "kim does not have access to add results for RunTime")
  
    def test_display_student_info(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("rob", "robpass", 1001)
      student = create_student("bob", "bobpass")
      comp = create_competition("RunTime", "rob")
      register_student("bob", "RunTime")
      add_results("rob", "bob", "RunTime", 15)
      self.assertListEqual(display_student_info("bob"), [{'id': 1, 'username': 'bob', 'role': 'Student', 'total points': 15, 'overall rank': 1}, [{'id': 1, 'name': 'RunTime'}]])

    def test_display_admin_info(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("kim", "kimpass", 1000)
      admin1 = create_admin("rob", "robpass", 1001)
      comp1 = create_competition('CodeSprint', 'kim')
      comp2 = create_competition('RunTime', 'rob')
      comp3 = create_competition('HashCode', 'rob')
      self.assertListEqual(display_admin_info("rob", 1001), [{'id': 2, 'username': 'rob', 'role': 'Admin', 'staff_id': 1001}, [{'id': 2, 'name': 'RunTime'}, {'id': 3, 'name': 'HashCode'}]])
  
    def test_competition_details(self):
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
      self.assertListEqual(display_competition_details(), [[{'id': 1, 'name': 'CodeSprint'}, [{'id': 1, 'user_id': 1, 'competition_id': 1, 'points_earned': 10}, {'id': 4, 'user_id': 2, 'competition_id': 1, 'points_earned': 10}, {'id': 9, 'user_id': 5, 'competition_id': 1, 'points_earned': 20}]], [{'id': 2, 'name': 'RunTime'}, [{'id': 2, 'user_id': 1, 'competition_id': 2, 'points_earned': 10}, {'id': 6, 'user_id': 3, 'competition_id': 2, 'points_earned': 15}, {'id': 8, 'user_id': 4, 'competition_id': 2, 'points_earned': 10}]], [{'id': 3, 'name': 'HashCode'}, [{'id': 3, 'user_id': 1, 'competition_id': 3, 'points_earned': 5}, {'id': 5, 'user_id': 2, 'competition_id': 3, 'points_earned': 10}, {'id': 7, 'user_id': 3, 'competition_id': 3, 'points_earned': 0}]]])

    def test_display_rankings(self):
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
          
      results = f'Rankings: Rank: 1\tStudent: ben\tPoints: 25 Rank: 2\tStudent: sally\tPoints: 20 Rank: 2\tStudent: amy\tPoints: 20 Rank: 4\tStudent: bob\tPoints: 15 Rank: 5\tStudent: jake\tPoints: 10 '
      self.assertEqual(display_rankings(), results)

    def test1_notify_student(self):
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

      add_results("rob", "bob", "HashCode", 15)
      self.assertEqual(notify_student("bob"), "bob has changed rankings to Rank 1")

    def test2_notify_student(self):
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

      display_student_info("bob")
      self.assertEqual(notify_student("bob"), "bob has not changed rankings")
