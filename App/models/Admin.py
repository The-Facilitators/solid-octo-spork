from App.database import db
from App.models import User, Competition

class Admin(User):
    __tablename__ = 'admin'
    staff_id = db.Column(db.Integer, unique=True)


    def __init__(self, username, password, staff_id):
        self.username = username
        self.set_password(password)
        self.staff_id = staff_id

    def add_Competition(self, name: str):
        new_Competition = Competition(name=name, creator_id=self.id)
        db.session.add(new_Competition)
        db.session.commit()
        
        return new_Competition


    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": 'admin'
        }

    def __repr__(self):
        return f'<Admin {self.id} : {self.username} >'