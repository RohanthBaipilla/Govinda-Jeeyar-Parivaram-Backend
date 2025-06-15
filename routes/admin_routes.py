from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app, db
from models import Admin, Volunteer, User
from datetime import datetime, timedelta

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
            created_date = datetime.fromisoformat(volunteer.createdAt.replace('Z', '+00:00'))
            if created_date.month == current_month and created_date.year == current_year:
                new_this_month += 1
    
    # Calculate active users (updated in last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    active_users = User.query.filter(User.updatedAt > thirty_days_ago).count()
    
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
