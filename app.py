from flask import Flask, jsonify
from config import Config
from extensions import jwt, bcrypt, mongo, cors
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.blog_routes import blog_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, origins="*")  # You can restrict this to your frontend URL later
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

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)