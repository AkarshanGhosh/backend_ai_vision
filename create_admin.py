from server.app import create_app
from server.models.user import User
from server.extensions import mongo

def create_admin():
    app = create_app()
    with app.app_context():
        print("Creating admin user...")
        username = input("Username: ")
        email = input("Email: ")
        password = input("Password: ")

        users = mongo.db.users
        if users.find_one({"email": email}):
            print("User already exists.")
            return

        admin = User(username, email, password, is_admin=True)
        users.insert_one(admin.to_dict())
        print("Admin created successfully!")

if __name__ == "__main__":
    create_admin()
