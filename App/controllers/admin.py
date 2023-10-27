from App.models import User, Admin, Competition

from App.database import db
from flask_jwt_extended import create_access_token


def create_Admin(username, password, staff_id):
    Here = Admin.query.filter_by(username=username).first()
    if Here:
        print(f'{username} already exists!')
        return Here  
    newA = Admin(username=username, password=password, staff_id=staff_id)
    try:
      db.session.add(newA)
      db.session.commit()
      print(f'New Admin: {username} created!')
    except Exception as e:
      db.session.rollback()
      print(f'Something went wrong creating {username}')
    return newA  


def get_admin_by_username(username):
    return Admin.query.filter_by(username=username).first()

def get_Admin(id):
    return Admin.query.get(id)

def get_all_admins():
    return Admin.query.all()

def get_all_admins_json():
    admins = Admin.query.all()
    if not admins:
        return []
    admins = [Admin.get_json() for Admin in admins]
    return admins

def update_Admin(id, username):
    Admin = get_Admin(id)
    if Admin:
        Admin.username = username
        db.session.add(Admin)
        return db.session.commit()
    return None

'''
We have an issue with the competitions created section
it looks for the creator ID but we actually used creator ID 
as the creator name in init so we could change it there or just 
pivot n use the ID as the name, I just changed the function
to search by username, it working that way
'''


def display_admin_info(username):
  admin = get_admin_by_username(username)
  competition = []
  if admin:
    comps = Competition.query.all()
    for comp in comps:
      if comp.creator_id == admin.staff_id:
        competition.append(comp.name)
    profile_info = {
        "profile": admin.get_json(),
        "competitions created": competition
    }
    return profile_info
  else:
    return None
