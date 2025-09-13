from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
from celery import Celery
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
migrate = Migrate()
celery = Celery()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///social_network.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
    print("JWT_SECRET_KEY:", app.config["JWT_SECRET_KEY"])
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    
    # Mail configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Celery configuration
    app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Celery
    celery.conf.update(app.config)
    
    # Import and register blueprints
    from app.api.auth import auth_bp
    from app.api.posts import posts_bp
    from app.api.users import users_bp
    from app.api.comments import comments_bp
    from app.api.media import media_bp
    from app.api.sms_auth import sms_auth_bp
    from app.api.email_auth import email_auth_bp
    from app.api.google_auth import google_auth_bp
    from app.api.unified_auth import unified_auth_bp
    
    app.register_blueprint(unified_auth_bp, url_prefix='/api/unified-auth')
    app.register_blueprint(google_auth_bp, url_prefix='/api/auth/google')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(sms_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(email_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(comments_bp, url_prefix='/api')
    app.register_blueprint(media_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        # Import all models to ensure they are registered
        from app.models.user import User
        from app.models.post import Post
        from app.models.like import Like
        from app.models.comment import Comment
        from app.models.media import Media
        from app.models.verification import PhoneVerification
        from app.models.code import Code
        from app.models.email_verification import EmailVerification
        try:
            db.create_all()
        except Exception as e:
            # Tables might already exist, this is not a critical error
            print(f"Database tables creation note: {e}")
            pass
        
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
    
    # Add route for serving uploaded files
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        """Serve uploaded files"""
        from flask import send_from_directory
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        return send_from_directory(uploads_dir, filename)
    
    return app
