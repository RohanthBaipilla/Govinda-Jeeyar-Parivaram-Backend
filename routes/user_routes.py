from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app, db
from models import User
import uuid

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_all_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@app.route('/api/users/<uid>', methods=['GET'])
@jwt_required()
def get_user(uid):
    user = User.query.get(uid)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@app.route('/api/users', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Name is required'}), 400
    
    # Generate new UID if not provided
    uid = data.get('uid', str(uuid.uuid4()))
    
    # Check if user already exists
    existing_user = User.query.get(uid)
    if existing_user:
        return jsonify({'message': 'User with this ID already exists'}), 409
    
    new_user = User(
        uid=uid,
        name=data.get('name'),
        dob=data.get('dob', ''),
        mobile=data.get('mobile', ''),
        whatsapp=data.get('whatsapp', ''),
        address=data.get('address', ''),
        maritalStatus=data.get('maritalStatus', 'single'),
        anniversaryDate=data.get('anniversaryDate', ''),
        createdBy=data.get('createdBy', ''),
        updatedBy=data.get('updatedBy', '')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(new_user.to_dict()), 201

@app.route('/api/users/<uid>', methods=['PUT'])
@jwt_required()
def update_user(uid):
    user = User.query.get(uid)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update user fields
    if 'name' in data:
        user.name = data['name']
    if 'dob' in data:
        user.dob = data['dob']
    if 'mobile' in data:
        user.mobile = data['mobile']
    if 'whatsapp' in data:
        user.whatsapp = data['whatsapp']
    if 'address' in data:
        user.address = data['address']
    if 'maritalStatus' in data:
        user.maritalStatus = data['maritalStatus']
    if 'anniversaryDate' in data:
        user.anniversaryDate = data['anniversaryDate']
    if 'updatedAt' in data:
        user.updatedAt = data['updatedAt']
    if 'updatedBy' in data:
        user.updatedBy = data['updatedBy']
    
    db.session.commit()
    
    return jsonify(user.to_dict()), 200

@app.route('/api/users/<uid>', methods=['DELETE'])
@jwt_required()
def delete_user(uid):
    user = User.query.get(uid)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200
