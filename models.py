from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
import pdb

bcrypt = Bcrypt
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)
    
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    department = db.relationship('Department', backref='users')

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    @classmethod
    def signup(cls, first_name, last_name, email, 
            password, department_id, admin=False):
        hashed_pw = generate_password_hash(password).decode('utf8')

        user = User(first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=hashed_pw,
                    department_id=department_id,
                    admin=admin)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter(cls.email == email).first()
        if user:
            is_auth = check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
        
class ACH(db.Model):
    __tablename__ = 'ach_credits'

    def __repr__(self):
        return f"<id: {self.id} amount: {self.amount} received: {self.received}>"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department = db.Column(db.Integer)
    amount = db.Column(db.Float, nullable=False)
    fund = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    received = db.Column(db.Date, nullable=False)

    roc_id = db.Column(db.Integer, db.ForeignKey('rocs.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    
    roc = db.relationship('ROC', backref='credits')
    department = db.relationship('Department', backref='credits')
    
class ROC(db.Model):
    __tablename__ = 'rocs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    roc = db.Column(db.LargeBinary, nullable=False)
    claimed = db.Column(db.Date, nullable=True)
    booked = db.Column(db.Date, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    user = db.relationship('User')
    docs = db.relationship('SupportingDoc', backref='roc', uselist=True)

class SupportingDoc(db.Model):
    __tablename__ = 'supp_docs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String, nullable=False)
    doc = db.Column(db.LargeBinary, nullable=False)
    roc_id = db.Column(db.Integer, db.ForeignKey('rocs.id'), nullable=True)
    
class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

