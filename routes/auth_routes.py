from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from bson.objectid import ObjectId

from extensions import mongo
from models.user import User

auth_bp = Blueprint('auth', __name__)


# Register new user
@auth_bp.route('/register', methods=['POST'])
def register():
    users = mongo.db.users
    data = request.get_json()

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email and password required'}), 400

    if users.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 409

    user = User(username, email, password)
    user_dict = user.to_dict()
    inserted = users.insert_one(user_dict)

    return jsonify({
        'message': 'User registered successfully',
        'user_id': str(inserted.inserted_id)
    }), 201

# Login
@auth_bp.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = users.find_one({'email': email})
    if not user or not User.check_password(user['password_hash'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    users.update_one({'_id': user['_id']}, {'$set': {
        'is_online': True,
        'last_seen': datetime.utcnow()
    }})

    access_token = create_access_token(identity=str(user['_id']))
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'is_admin': user.get('is_admin', False)
        }
    }), 200

# Logout
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    users = mongo.db.users
    user_id = get_jwt_identity()
    users.update_one({'_id': ObjectId(user_id)}, {'$set': {'is_online': False}})
    return jsonify({'message': 'Logout successful'}), 200

# Get profile
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    users = mongo.db.users
    user_id = get_jwt_identity()
    user = users.find_one({'_id': ObjectId(user_id)})

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'is_admin': user.get('is_admin', False),
            'is_online': user.get('is_online', False),
            'created_at': user['created_at'].isoformat()
        }
    }), 200
