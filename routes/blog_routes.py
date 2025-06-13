from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime

from server.extensions import mongo
from server.utils.decorators import admin_required
from server.models.blog import Blog

blog_bp = Blueprint('blog', __name__)


# Public: Get all blogs
@blog_bp.route('/blogs', methods=['GET'])
def get_all_blogs():
    blogs = mongo.db.blogs
    users = mongo.db.users
    blog_docs = blogs.find().sort("created_at", -1)
    results = []
    for blog in blog_docs:
        author = users.find_one({'_id': ObjectId(blog['author_id'])})
        author_name = author['username'] if author else "Unknown"
        results.append({
            'id': str(blog['_id']),
            'title': blog['title'],
            'content': blog['content'],
            'author': author_name,
            'created_at': blog['created_at'].isoformat(),
            'updated_at': blog['updated_at'].isoformat()
        })
    return jsonify({'blogs': results}), 200

# Public: Get single blog by ID
@blog_bp.route('/blogs/<blog_id>', methods=['GET'])
def get_blog(blog_id):
    blogs = mongo.db.blogs
    users = mongo.db.users
    blog = blogs.find_one({'_id': ObjectId(blog_id)})
    if not blog:
        return jsonify({'error': 'Blog not found'}), 404

    author = users.find_one({'_id': ObjectId(blog['author_id'])})
    author_name = author['username'] if author else "Unknown"

    return jsonify({
        'blog': {
            'id': str(blog['_id']),
            'title': blog['title'],
            'content': blog['content'],
            'author': author_name,
            'created_at': blog['created_at'].isoformat(),
            'updated_at': blog['updated_at'].isoformat()
        }
    }), 200

# Admin-only: Create new blog
@blog_bp.route('/blogs', methods=['POST'])
@jwt_required()
@admin_required
def create_blog():
    blogs = mongo.db.blogs
    users = mongo.db.users
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    author_id = get_jwt_identity()

    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400

    blog = Blog(title=title, content=content, author_id=author_id)
    blog_id = blogs.insert_one(blog.to_dict()).inserted_id

    return jsonify({'message': 'Blog created', 'blog_id': str(blog_id)}), 201

# Admin-only: Update blog
@blog_bp.route('/blogs/<blog_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_blog(blog_id):
    blogs = mongo.db.blogs
    users = mongo.db.users
    data = request.get_json()
    updates = {}

    if 'title' in data:
        updates['title'] = data['title'].strip()
    if 'content' in data:
        updates['content'] = data['content'].strip()

    if not updates:
        return jsonify({'error': 'No update fields provided'}), 400

    updates['updated_at'] = datetime.utcnow()

    result = blogs.update_one({'_id': ObjectId(blog_id)}, {'$set': updates})

    if result.matched_count == 0:
        return jsonify({'error': 'Blog not found'}), 404

    return jsonify({'message': 'Blog updated'}), 200

# Admin-only: Delete blog
@blog_bp.route('/blogs/<blog_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_blog(blog_id):
    blogs = mongo.db.blogs
    users = mongo.db.users
    result = blogs.delete_one({'_id': ObjectId(blog_id)})

    if result.deleted_count == 0:
        return jsonify({'error': 'Blog not found'}), 404

    return jsonify({'message': 'Blog deleted'}), 200
