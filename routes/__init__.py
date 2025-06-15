from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app_init import app, db
from models import User, Volunteer, Admin
import uuid
from datetime import datetime, timedelta

# Auth routes - ensure all routes are prefixed with /api
@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
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

# Add a route to handle OPTIONS requests explicitly
@app.route('/api/auth/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    # Debug output
    print(f"Signup attempt for email: {email}")
    
    # Check if user already exists with more detailed error
    existing_admin = Admin.query.filter_by(email=email).first()
    if existing_admin:
        print(f"Email {email} already exists as admin")
        return jsonify({'message': 'Email already registered', 'role': 'admin'}), 409
    
    existing_volunteer = Volunteer.query.filter_by(email=email).first()
    if existing_volunteer:
        print(f"Email {email} already exists as volunteer")
        return jsonify({'message': 'Email already registered', 'role': 'volunteer'}), 409
    
    try:
        # Create new volunteer with a new UID
        new_uid = str(uuid.uuid4())
        volunteer = Volunteer(
            uid=new_uid,
            email=email,
            name=data.get('name', email.split('@')[0]),
            password_hash=generate_password_hash(password),
            createdAt=datetime.now().isoformat(),
            updatedAt=datetime.now().isoformat(),
            role='volunteer'
        )
        
        db.session.add(volunteer)
        db.session.commit()
        
        print(f"Successfully created volunteer with email: {email}, uid: {new_uid}")
        
        token = create_access_token(identity={'uid': new_uid, 'role': 'volunteer'})
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {
                'uid': new_uid,
                'email': email,
                'role': 'volunteer'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating volunteer: {str(e)}")
        return jsonify({'message': f'Error creating user: {str(e)}'}), 500

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

# Admin routes
@app.route('/api/admin/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    # Verify admin role
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Get total volunteers
    total_volunteers = Volunteer.query.count()
    
    # Get total users
    total_users = User.query.count()
    
    # Calculate new this month
    current_month = datetime.now().month
    current_year = datetime.now().year
    new_this_month = 0
    
    volunteers = Volunteer.query.all()
    for volunteer in volunteers:
        if volunteer.createdAt:
            try:
                created_date = datetime.fromisoformat(volunteer.createdAt.replace('Z', '+00:00'))
                if created_date.month == current_month and created_date.year == current_year:
                    new_this_month += 1
            except ValueError:
                # Skip if date format is invalid
                pass
    
    # Calculate active users (updated in last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    
    active_users = 0
    users = User.query.all()
    for user in users:
        if user.updatedAt and user.updatedAt > thirty_days_ago:
            active_users += 1
    
    return jsonify({
        'totalVolunteers': total_volunteers,
        'totalUsers': total_users,
        'newThisMonth': new_this_month,
        'activeUsers': active_users
    }), 200

@app.route('/api/admin/profile', methods=['GET'])
@jwt_required()
def get_admin_profile():
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    admin = Admin.query.get(current_user.get('uid'))
    if not admin:
        return jsonify({'message': 'Admin profile not found'}), 404
    
    return jsonify(admin.to_dict()), 200

@app.route('/api/admin/profile', methods=['PUT'])
@jwt_required()
def update_admin_profile():
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    admin = Admin.query.get(current_user.get('uid'))
    if not admin:
        # Create new admin profile if it doesn't exist
        admin = Admin(
            uid=current_user.get('uid'),
            name='Admin',
            email='admin@example.com'
        )
        db.session.add(admin)
    
    data = request.get_json()
    
    # Update admin fields
    if 'name' in data:
        admin.name = data['name']
    if 'dob' in data:
        admin.dob = data['dob']
    if 'mobile' in data:
        admin.mobile = data['mobile']
    if 'whatsapp' in data:
        admin.whatsapp = data['whatsapp']
    if 'address' in data:
        admin.address = data['address']
    if 'updatedAt' in data:
        admin.updatedAt = data['updatedAt']
    
    db.session.commit()
    
    return jsonify(admin.to_dict()), 200

# User routes
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

# Add more routes for Volunteer API
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
    
    new_volunteer = Volunteer(
        uid=uid,
        name=data.get('name'),
        email=data.get('email'),
        dob=data.get('dob', ''),
        mobile=data.get('mobile', ''),
        whatsapp=data.get('whatsapp', ''),
        address=data.get('address', ''),
        maritalStatus=data.get('maritalStatus', 'single'),
        anniversaryDate=data.get('anniversaryDate', ''),
        createdAt=data.get('createdAt', datetime.now().isoformat()),
        updatedAt=data.get('updatedAt', datetime.now().isoformat()),
        createdBy=data.get('createdBy', 'admin'),
        role='volunteer'
    )
    
    if data.get('password'):
        new_volunteer.password_hash = generate_password_hash(data.get('password'))
    
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
        volunteer.password_hash = generate_password_hash(data['password'])
    
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

# User CRUD routes
@app.route('/api/users', methods=['POST'])
@jwt_required()
def create_user():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Name is required'}), 400
    
    # Generate new UID if not provided
    uid = data.get('uid', str(uuid.uuid4()))
    
    # Check if user already exists
    existing_user = User.query.get(uid)
    if existing_user:
        return jsonify({'message': 'User with this ID already exists'}), 409
    
    # Set default creator based on current user role
    creator = data.get('createdBy', '')
    if not creator:
        if current_user.get('role') == 'admin':
            creator = 'admin'
        else:
            creator = current_user.get('email', 'volunteer')
    
    new_user = User(
        uid=uid,
        name=data.get('name'),
        dob=data.get('dob', ''),
        mobile=data.get('mobile', ''),
        whatsapp=data.get('whatsapp', ''),
        address=data.get('address', ''),
        maritalStatus=data.get('maritalStatus', 'single'),
        anniversaryDate=data.get('anniversaryDate', ''),
        createdAt=data.get('createdAt', datetime.now().isoformat()),
        updatedAt=data.get('updatedAt', datetime.now().isoformat()),
        createdBy=creator,
        updatedBy=creator
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
