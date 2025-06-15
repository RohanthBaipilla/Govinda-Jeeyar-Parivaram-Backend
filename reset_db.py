from app_init import app, db

def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("All tables dropped.")
        
        # Recreate all tables
        db.create_all()
        print("Database tables recreated.")
        
        print("Database has been reset. Run setup.py to create an admin user.")

if __name__ == '__main__':
    reset_database()
