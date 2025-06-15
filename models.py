from app_init import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    uid = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    address = db.Column(db.Text)
    maritalStatus = db.Column(db.String(20), default='single')
    anniversaryDate = db.Column(db.String(20))
    createdAt = db.Column(db.String(30), default=lambda: datetime.now().isoformat())
    updatedAt = db.Column(db.String(30), default=lambda: datetime.now().isoformat())
    createdBy = db.Column(db.String(100))
    updatedBy = db.Column(db.String(100))

    def to_dict(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'dob': self.dob,
            'mobile': self.mobile,
            'whatsapp': self.whatsapp,
            'address': self.address,
            'maritalStatus': self.maritalStatus,
            'anniversaryDate': self.anniversaryDate,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            'createdBy': self.createdBy,
            'updatedBy': self.updatedBy
        }

class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    
    uid = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    dob = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    address = db.Column(db.Text)
    maritalStatus = db.Column(db.String(20), default='single')
    anniversaryDate = db.Column(db.String(20))
    createdAt = db.Column(db.String(30), default=lambda: datetime.now().isoformat())
    updatedAt = db.Column(db.String(30), default=lambda: datetime.now().isoformat())
    createdBy = db.Column(db.String(100), default='admin')
    role = db.Column(db.String(20), default='volunteer')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'email': self.email,
            'dob': self.dob,
            'mobile': self.mobile,
            'whatsapp': self.whatsapp,
            'address': self.address,
            'maritalStatus': self.maritalStatus,
            'anniversaryDate': self.anniversaryDate,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            'createdBy': self.createdBy,
            'role': self.role
        }

class Admin(db.Model):
    __tablename__ = 'admins'
    
    uid = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    dob = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    address = db.Column(db.Text)
    updatedAt = db.Column(db.String(30), default=lambda: datetime.now().isoformat())
    role = db.Column(db.String(20), default='admin')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'email': self.email,
            'dob': self.dob,
            'mobile': self.mobile,
            'whatsapp': self.whatsapp,
            'address': self.address,
            'updatedAt': self.updatedAt,
            'role': self.role
        }
