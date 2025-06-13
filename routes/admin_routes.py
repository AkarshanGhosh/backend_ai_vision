from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from datetime import datetime

from extensions import mongo, bcrypt
from models.user import User
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)


# ✅ Get all users (fixed return format)
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    users = mongo.db.users
    try:
        user_docs = users.find()
        result = []
        for user in user_docs:
            result.append({
                'id': str(user['_id']),
                'username': user.get('username'),
                'email': user.get('email'),
                'is_admin': user.get('is_admin', False),
                'is_online': user.get('is_online', False),
                'created_at': user.get('created_at', datetime.utcnow()).isoformat(),
                'last_seen': user.get('last_seen', datetime.utcnow()).isoformat()
            })
        return jsonify(result), 200  # ✅ now returns a direct list
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ✅ Add user
@admin_bp.route('/users', methods=['POST'])
@jwt_required()
@admin_required
def add_user():
    users = mongo.db.users
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if users.find_one({'email': email}):
        return jsonify({'error': 'Email already exists'}), 409

    user = User(username, email, password, is_admin=data.get('is_admin', False))
    users.insert_one(user.to_dict())

    return jsonify({'message': 'User added successfully'}), 201


# ✅ Delete user
@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    users = mongo.db.users
    result = users.delete_one({'_id': ObjectId(user_id)})
    if result.deleted_count == 0:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'User deleted successfully'}), 200


# ✅ Update user password
@admin_bp.route('/users/<user_id>/password', methods=['PUT'])
@jwt_required()
@admin_required
def update_password(user_id):
    users = mongo.db.users
    data = request.get_json()
    new_password = data.get('new_password', '')

    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    result = users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'password_hash': new_hash}}
    )

    if result.modified_count == 0:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'message': 'Password updated successfully'}), 200


# ✅ User stats (fixed camelCase keys)
@admin_bp.route('/users/stats', methods=['GET'])
@jwt_required()
@admin_required
def user_stats():
    users = mongo.db.users
    try:
        online_count = users.count_documents({'is_online': True})
        offline_count = users.count_documents({'is_online': False})
        total = online_count + offline_count
        return jsonify({
            'totalUsers': total,
            'onlineUsers': online_count,
            'offlineUsers': offline_count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ✅ Update user (general update endpoint)    
@admin_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    users = mongo.db.users
    data = request.get_json()
    update_fields = {}

    new_username = data.get('username')
    new_password = data.get('password')

    if new_username:
        update_fields['username'] = new_username.strip()

    if new_password:
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
        update_fields['password_hash'] = hashed_pw

    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400

    result = users.update_one({'_id': ObjectId(user_id)}, {'$set': update_fields})

    if result.modified_count == 0:
        return jsonify({'error': 'User not found or no changes made'}), 404

    return jsonify({'message': 'User updated successfully'}), 200