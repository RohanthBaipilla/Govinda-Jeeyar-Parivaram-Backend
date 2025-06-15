from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import Volunteer, Admin
import uuid

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    # Check if user is an admin
    admin = Admin.query.filter_by(email=email).first()
    if admin and check_password_hash(admin.password_hash, password):
        token = create_access_token(identity={'uid': admin.uid, 'role': 'admin'})
        return jsonify({
            'token': token,
            'user': {
                'uid': admin.uid,
                'email': admin.email,
                'role': 'admin'
            }
        }), 200
    
    # Check if user is a volunteer
    volunteer = Volunteer.query.filter_by(email=email).first()
    if volunteer and check_password_hash(volunteer.password_hash, password):
        token = create_access_token(identity={'uid': volunteer.uid, 'role': 'volunteer'})
        return jsonify({
            'token': token,
            'user': {
                'uid': volunteer.uid,
                'email': volunteer.email,
                'role': 'volunteer'
            }
        }), 200
    
    return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    # Check if user already exists
    if Admin.query.filter_by(email=email).first() or Volunteer.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 409
    
    # Create new volunteer
    new_uid = str(uuid.uuid4())
    volunteer = Volunteer(
        uid=new_uid,
        email=email,
        name=data.get('name', email.split('@')[0])  # Default name to email username if not provided
    )
    volunteer.set_password(password)
    
    db.session.add(volunteer)
    db.session.commit()
    
    token = create_access_token(identity={'uid': volunteer.uid, 'role': 'volunteer'})
    
    return jsonify({
        'message': 'User created successfully',
        'token': token,
        'user': {
            'uid': volunteer.uid,
            'email': volunteer.email,
            'role': 'volunteer'
        }
    }), 201

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user = get_jwt_identity()
    uid = current_user.get('uid')
    role = current_user.get('role')
    
    if role == 'admin':
        user = Admin.query.get(uid)
    else:
        user = Volunteer.query.get(uid)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'uid': user.uid,
        'email': user.email,
        'role': role
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    # JWT tokens are stateless, so we don't actually invalidate them server-side
    # The client will remove the token from storage
    return jsonify({'message': 'Logged out successfully'}), 200
