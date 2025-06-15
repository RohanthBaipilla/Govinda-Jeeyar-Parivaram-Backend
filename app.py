from app_init import app, db
from models import User, Volunteer, Admin
import routes

# Create routes folder and __init__.py
# The routes will be initialized in the routes/__init__.py file

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables before running the app
    app.run(debug=True)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Import models
from models import User, Volunteer, Admin

# Import routes
from routes import auth_routes, user_routes, volunteer_routes, admin_routes

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables before running the app
    app.run(debug=True)
