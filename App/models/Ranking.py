from App.database import db
from App.models import Participation

class Ranking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('Student.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    #competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    total_points = db.Column(db.Integer, nullable=False)  # Total points earned by the user

    def update_total_points(self):
        user_participations = Participation.query.filter_by(user_id=self.user_id, competition_id=self.competition_id).all()
        total_points = sum(participation.points_earned for participation in user_participations)
        self.total_points = total_points
