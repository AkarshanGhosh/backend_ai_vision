from flask import Flask, jsonify
from server.config import Config
from server.extensions import jwt, bcrypt, mongo, cors
from server.routes.auth_routes import auth_bp
from server.routes.admin_routes import admin_bp
from server.routes.blog_routes import blog_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    jwt.init_app(app)
    bcrypt.init_app(app)
    mongo.init_app(app)
    cors.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(blog_bp, url_prefix='/api/blog')

    # Optional: Home route for quick confirmation
    @app.route('/')
    def home():
        return jsonify({'message': 'Backend is running ✅'}), 200

    # Optional: Health check route for monitoring
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'}), 200

    return app
