from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app, db
from models import Volunteer
import uuid

@app.route('/api/volunteers', methods=['GET'])
@jwt_required()
def get_all_volunteers():
    # Check if user is admin
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    volunteers = Volunteer.query.all()
    return jsonify([volunteer.to_dict() for volunteer in volunteers]), 200

@app.route('/api/volunteers/<uid>', methods=['GET'])
@jwt_required()
def get_volunteer(uid):
    current_user = get_jwt_identity()
    
    # Allow volunteers to view their own data or admins to view any volunteer
    if current_user.get('role') != 'admin' and current_user.get('uid') != uid:
        return jsonify({'message': 'Unauthorized'}), 403
    
    volunteer = Volunteer.query.get(uid)
    if not volunteer:
        return jsonify({'message': 'Volunteer not found'}), 404
    
    return jsonify(volunteer.to_dict()), 200

@app.route('/api/volunteers', methods=['POST'])
@jwt_required()
def create_volunteer():
    current_user = get_jwt_identity()
    
    # Only allow admins to create volunteers
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'message': 'Name and email are required'}), 400
    
    # Check if email is already in use
    if Volunteer.query.filter_by(email=data.get('email')).first():
        return jsonify({'message': 'Email already in use'}), 409
    
    # Generate new UID if not provided
    uid = data.get('uid', str(uuid.uuid4()))
    
    # Create password hash if password is provided
    password_hash = None
    if data.get('password'):
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(data.get('password'))
    
    new_volunteer = Volunteer(
        uid=uid,
        name=data.get('name'),
        email=data.get('email'),
        password_hash=password_hash,
        dob=data.get('dob', ''),
        mobile=data.get('mobile', ''),
        whatsapp=data.get('whatsapp', ''),
        address=data.get('address', ''),
        maritalStatus=data.get('maritalStatus', 'single'),
        anniversaryDate=data.get('anniversaryDate', ''),
        createdAt=data.get('createdAt', ''),
        updatedAt=data.get('updatedAt', ''),
        createdBy=data.get('createdBy', 'admin'),
        role='volunteer'
    )
    
    db.session.add(new_volunteer)
    db.session.commit()
    
    return jsonify(new_volunteer.to_dict()), 201

@app.route('/api/volunteers/<uid>', methods=['PUT'])
@jwt_required()
def update_volunteer(uid):
    current_user = get_jwt_identity()
    
    # Allow volunteers to update their own data or admins to update any volunteer
    if current_user.get('role') != 'admin' and current_user.get('uid') != uid:
        return jsonify({'message': 'Unauthorized'}), 403
    
    volunteer = Volunteer.query.get(uid)
    if not volunteer:
        return jsonify({'message': 'Volunteer not found'}), 404
    
    data = request.get_json()
    
    # Update volunteer fields
    if 'name' in data:
        volunteer.name = data['name']
    if 'email' in data and current_user.get('role') == 'admin':  # Only admin can change email
        volunteer.email = data['email']
    if 'dob' in data:
        volunteer.dob = data['dob']
    if 'mobile' in data:
        volunteer.mobile = data['mobile']
    if 'whatsapp' in data:
        volunteer.whatsapp = data['whatsapp']
    if 'address' in data:
        volunteer.address = data['address']
    if 'maritalStatus' in data:
        volunteer.maritalStatus = data['maritalStatus']
    if 'anniversaryDate' in data:
        volunteer.anniversaryDate = data['anniversaryDate']
    if 'updatedAt' in data:
        volunteer.updatedAt = data['updatedAt']
    
    # Update password if provided
    if 'password' in data and data['password']:
        volunteer.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify(volunteer.to_dict()), 200

@app.route('/api/volunteers/<uid>', methods=['DELETE'])
@jwt_required()
def delete_volunteer(uid):
    current_user = get_jwt_identity()
    
    # Only allow admins to delete volunteers
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    volunteer = Volunteer.query.get(uid)
    if not volunteer:
        return jsonify({'message': 'Volunteer not found'}), 404
    
    db.session.delete(volunteer)
    db.session.commit()
    
    return jsonify({'message': 'Volunteer deleted successfully'}), 200
