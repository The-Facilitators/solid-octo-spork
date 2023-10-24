from App.database import db
from App.models import User, Participation, Competition

class Student(User):
    __tablename__ = "student"
    competitions = db.relationship('Competition', secondary="participation", overlaps='participants', lazy=True)
    points = db.Column(db.Integer, default=0)
    ranking = db.Column(db.Integer, nullable=False, default=0)
    previous_ranking = db.Column(db.Integer, nullable=False, default=0)
    
    """def participate_in_competition(self, competition):
        if isinstance(self, Student):
            participation = Participation(user=self, competition=competition)
            db.session.add(participation)
            db.session.commit()
            return participation
        else:
            return None"""

    def participate_in_competition(self, competition):
        registered = False
        for comp in self.competitions:
          if (comp.id == competition.id):
            registered = True
            
        if isinstance(self, Student) and not registered:
            participation = Participation(user_id=self.id, competition_id=competition.id)
            try:
              self.competitions.append(competition)
              competition.participants.append(self)
              #db.session.add(self)
              #db.session.add(competition)
              #db.session.add(participation)
              db.session.commit()
            except Exception as e:
              db.session.rollback()
              return None
            else:
              print(f'{self.username} was registered for {competition.name}')
              return participation
        else:
            print(f'{self.username} is already registered for {competition.name}')
            return None
    
    """def add_Competition_to_student(self, student_id: int, competition_id: int):
        student = self.get_student(student_id)
        competition = self.get_competition(competition_id)
        if student and competition:
            student.competitions.append(competition)
            db.session.add(student)
            db.session.commit()
            return student
        else:
            return None"""

    def set_points(self, points):
      self.points = points

    def set_ranking(self, ranking):
      self.ranking = ranking

    def set_previous_ranking(self, ranking):
      self.previous_ranking = ranking
    
    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "point": self.points
        }

    """def __repr__(self):
        return f'<Student {self.id} : {self.username}>'"""
    def __repr__(self):
        return f'<Student {self.id} : {self.username}>'
