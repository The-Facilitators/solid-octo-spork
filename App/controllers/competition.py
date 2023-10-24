from App.models import User, Competition, Participation

from App.database import db
from flask_jwt_extended import create_access_token

"""def create_Competition(name, creator_id):
    newComp = Competition(name=name, creator_id=creator_id)
    try:
      db.session.add(newComp)
      db.session.commit()
    except Exception as e:
      db.session.rollback()
      #print(str(e))
      print(f'{name} already exists!')
    else:
      print(f'{name} created!')
    return newComp
"""
def create_Competition(name, creator_id):
    Here= Competition.query.filter_by(name=name).first()
    if Here:
        print(f'{name} already exists!')
        return Here
    newComp = Competition(name=name, creator_id=creator_id)
    try:
      db.session.add(newComp)
      db.session.commit()
      print(f'{name} created!')
    except Exception as e:
      db.session.rollback()
      print(f'Something went wrong creating {name}')
    return newComp

def get_competition(id):
  return Competition.query.get(id)

def get_all_competitions():
    comps=Competition.query.all()
    if not comps:
        return "No competitions found"
    else:
        comp=[Competition.get_json() for Competition in comps]
        return comp

def get_all_participations():
    participants=Participation.query.all()
    if not participants:
        return "No participants found"
    else:
        participant=[Participation.get_json() for Participation in participants]
        return participant
