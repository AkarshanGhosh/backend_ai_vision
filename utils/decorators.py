from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from bson.objectid import ObjectId  # ✅ Required for correct MongoDB ID matching
from server.database import Database

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        try:
            user = Database.get_users_collection().find_one({"_id": ObjectId(user_id)})
        except Exception:
            return jsonify({'error': 'Invalid user ID format'}), 400

        if not user or not user.get("is_admin"):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return wrapper
