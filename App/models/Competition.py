from App.database import db

class Competition(db.Model):
    __tablename__='competition'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    participants = db.relationship('Student', secondary="participation", overlaps='competetions', lazy=True)

    def __init__(self, name, creator_id):
      self.name = name
      self.creator_id = creator_id
    
    def get_json(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "creator_id": self.creator_id,
            "participants": [student.username for student in self.participants]
        }
    

    def __repr__(self):
        return f'<Competition {self.id} : {self.name}>'
