from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def db_connect(app):
    db.app = app
    db.init_app()
    
class User:
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    department = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    # clearance = db.Column(db.Intger, nullable=False, default=1)
    
    claimed = db.relationship('ACH', db.ForeignKey('ach_credits'), backref='user')
    clearance = db.relationship(db.Integer, db.ForeignKey('clearances.clearance'), backref='users')
    
class ACH:
    __tablename__ = 'ach_credits'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float, nullable=False)
    fund = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    received = db.Column(db.Date, nullable=False)
    claimed = db.Column(db.DateTime)
    booked = db.Column(db.DateTime)
    # status = db.Column(db.Integer, nullable=False, default=1)
    
    status = db.relationship('Status', db.ForeignKey('statuses'))
    file = db.relationship('ROC', db.ForeignKey('files'), backref='credit')
    
class File:
    __tablename__ = 'files'
    
    id = db.Column()
    filename = db.Column(db.String, nullable=False)
    file = db.Column(db.LargeBinary, nullable=False)
    user = db.relationship('User', db.ForeignKey('users'))
    
class Status:
    __tablename__ = 'statuses'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Integer, nullable=False)
    
class Clearance:
    __tablename__ = 'clearances'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clearance = db.Column(db.Integer, nullable=False)