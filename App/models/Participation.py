from App.database import db

class Participation(db.Model):
    __tablename__='participation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    points_earned = db.Column(db.Integer, nullable=True)


    def __init__(self, user_id, competition_id, rank):
        self.user_id = user_id
        self.competition_id = competition_id
        self.rank = rank
        self.points_earned = 0


    # user = db.relationship('Student', back_populates='Competed_In')
    # competition = db.relationship('Competition', back_populates='participants')

    def get_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'competition_id': self.competition_id,
            'rank': self.rank,
            'points_earned': self.calculate_points()
        }