from flask_login import login_user, login_manager, logout_user, LoginManager
from flask_jwt_extended import create_access_token, jwt_required, JWTManager,get_jwt_identity


from App.models import User, Admin, Student



def jwt_authenticate(username, password):
    student = Student.query.filter_by(username=username).first()
    admin = Admin.query.filter_by(username=username).first()
    if student and student.check_password(password):
        return create_access_token(identity=username)
    elif admin and admin.check_password(password):
        return create_access_token(identity=username)
    return None

def login(username, password):
    student = Student.query.filter_by(username=username).first()
    admin = Admin.query.filter_by(username=username).first()
    if student:
        if student.check_password(password):
           # login_user(student)
            return student
    elif admin:
        if admin.check_password(password):
           # login_user(admin)
            return admin
    return None
    return None


'''def login(username, password):
    staff = Staff.query.filter_by(username=username).first()
    if staff and staff.check_password(password):
        return staff
    customer = Customer.query.filter_by(username=username).first()
    if customer and customer.check_password(password):
        return customer
    return None
'''
def login_Student(username, password):
    student = Student.query.filter_by(username=username).first()
    if student and student.check_password(password):
        login_user(student)
        return student
    return None

def login_Admin(username, password):
    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.check_password(password):
        login_user(admin)
        return admin
    return None

def setup_flask_login(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        student = Student.query.get(user_id)
        if student:
            return student

        admin = Admin.query.get(user_id)
        if admin:
            return admin

        return None  

    return login_manager
    

def setup_jwt(app):
    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        student = Student.query.filter_by(username=identity).one_or_none()
        admin = Admin.query.filter_by(username=identity).one_or_none()
        if student:
            return student.id
        elif admin:
            return admin.id
        return None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return Student.query.get(identity) or Admin.query.get(identity)

    return jwt



#########################################################################




def Student_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Student):
            return "Unauthorized", 401
        return func(*args, **kwargs)
    return wrapper

def Admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            return "Unauthorized", 401
        return func(*args, **kwargs)
    return wrapper