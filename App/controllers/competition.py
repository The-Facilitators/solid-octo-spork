from App.models import User, Competition, Participation,Admin

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
    admin= Admin.query.filter_by(username=creator_id).first()

    if not admin:
      return None

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
      return None
    return newComp

def get_competition(id):
  return Competition.query.get(id)

def get_all_competitions():
    comps=Competition.query.all()
    if not comps:
        return "No competitions found"
    else:
        return comps

def print_all_competitions():
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
        return participants

def print_all_participations():
    participants=Participation.query.all()
    if not participants:
        return "No participants found"
    else:
        participant=[Participation.get_json() for Participation in participants]
        return participant


'''
The get_all_competitions  n get_all_participants function returns a dictionary but we need 
an object for this function to work, I changed the functions so it to only returns the objects
the inital functions were renamed to print_all_competitions n print_all_participations  
'''
def display_competition_details():
  comps = get_all_competitions()
  results = []
  if not comps:
    print("No competitions found!")
  else:
    for comp in comps:
      competition = []
      participations = []
      print(comp.get_json())
      competition.append(comp.get_json())
      participants = Participation.query.filter_by(competition_id=comp.id).all()

      if not participants:
        print("No participants found!")
      else:
        for participant in participants:
          print(participant.get_json())
          participations.append(participant.get_json())
      competition.append(participations)
      results.append(competition)
  return results
