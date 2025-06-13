from datetime import datetime
from server.extensions import bcrypt

class User:
    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.is_admin = is_admin
        self.is_online = False
        self.created_at = datetime.utcnow()
        self.last_seen = datetime.utcnow()

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def check_password(stored_hash, password):
        return bcrypt.check_password_hash(stored_hash, password)
