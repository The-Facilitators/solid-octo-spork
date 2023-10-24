import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import Student, Admin
from App.controllers import *


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UnitTests(unittest.TestCase):
   
   'Student Unit Test
   def test_new_student(self):
        student = Student("bob", "bobpass")
        assert student.username == "bob"

   def test_set_points(self):
        student = Student("bob", "bobpass")
        student.set_points(15)
        assert student.points == 15
      
   def test_set_ranking(self):
        student = Student("bob", "bobpass")
        student.set_points(10)
        assert student.points == 10
    
   def test_previous_ranking(self):
      student = Student("bob", "bobpass")
      student.set_points(10)
      student.set_previous_ranking(student.points)
      student.set_points(5)
      assert student.previous_ranking == 10
  
   'Admin Unit Test
   def test_new_admin(self):
    admin = Admin("rob", "robpass", 1001)
    assert admin.username == "rob" and admin.staff_id == 1001

   'Competition Unit Test
   def test_new_competition(self):
      competition = Competition("Comp", 1001)
      assert competition.name == "Comp"


    # pure function no side effects or integrations called
   def test_get_json(self):
       user = User("bob", "bobpass")
       user_json = user.get_json()
       self.assertDictEqual(user_json, {"id":None, "username":"bob"})
    
   def test_hashed_password(self):
       password = "mypass"
       hashed = generate_password_hash(password, method='sha256')
       user = User("bob", password)
       assert user.password != password

   def test_check_password(self):
       password = "mypass"
       user = User("bob", password)
       assert user.check_password(password)

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


def test_authenticate():
    user = create_user("bob", "bobpass")
    assert login("bob", "bobpass") != None

class IntegrationTests(unittest.TestCase):

    def test_create_user(self):
        user = create_user("rick", "bobpass")
        assert user.username == "rick"

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        self.assertListEqual([{"id":1, "username":"bob"}, {"id":2, "username":"rick"}], users_json)

    # Tests data changes in the database
    def test_update_user(self):
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"
