from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from App.models import db
from App.controllers import * 

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')

@index_views.route('/init', methods=['GET'])
def init():
    db.drop_all()
    db.create_all()
    create_Admin('Kim', 'Possible',33)
    create_Admin('Dr', 'robpass', 991)
    create_Student('sally', 'sallypass')
    create_Student('robin', 'Hood')
    create_Competition('RunTime',33)
    create_Competition('SuperSprint',991)
    print( 'database intialized' )
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})