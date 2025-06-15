import os
from flask_jwt_extended import JWTManager
from app_init import app, db

# App Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Import models (so Flask can detect them during db.create_all)
from models import User, Volunteer, Admin

# Import routes to register them (assuming Blueprints are used in routes/__init__.py)
import routes

# Run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
