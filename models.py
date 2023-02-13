from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)
    
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    department = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    # clearance = db.Column(db.Intger, nullable=False, default=1)
    
    # claimed = db.relationship('ACH', db.ForeignKey('ach_credits'), backref='user')
    # clearance = db.relationship(db.Integer, db.ForeignKey('clearances.clearance'), backref='users')
    
class ACH(db.Model):
    __tablename__ = 'ach_credits'

    def __repr__(self):
        return f"<id: {self.id} amount: {self.amount} received: {self.received} claimed: {self.claimed} booked: {self.booked}>"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department = db.Column(db.Integer)
    amount = db.Column(db.Float, nullable=False)
    fund = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    received = db.Column(db.Date, nullable=False)
    claimed = db.Column(db.DateTime)
    booked = db.Column(db.DateTime)
    # status = db.Column(db.Integer, nullable=False, default=1)
    
    # status = db.relationship('Status', db.ForeignKey('statuses'))
    # file = db.relationship('ROC', db.ForeignKey('files'), backref='credit')
    
class ROC(db.Model):
    __tablename__ = 'rocs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String, nullable=False)
    roc = db.Column(db.LargeBinary, nullable=False)
    # user = db.relationship('User', db.ForeignKey('users'))

class SupportingDoc(db.Model):
    __tablename__ = 'supporting_documentation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String, nullable=False)
    doc = db.Column(db.LargeBinary, nullable=False)
    
class Status(db.Model):
    __tablename__ = 'status_codes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Integer, nullable=False)
    
class Clearance(db.Model):
    __tablename__ = 'clearances'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clearance = db.Column(db.Integer, nullable=False)