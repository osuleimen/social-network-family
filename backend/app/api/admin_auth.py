from flask import Blueprint, request, jsonify, render_template_string
from flask_jwt_extended import create_access_token, create_refresh_token
from app import db
from app.models.user import User, UserRole
import logging

logger = logging.getLogger(__name__)

admin_auth_bp = Blueprint('admin_auth', __name__)

# HTML template for admin login form
ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - GrampsWeb Social Network</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-header h1 {
            color: #333;
            margin: 0;
            font-size: 1.8rem;
        }
        .login-header p {
            color: #666;
            margin: 0.5rem 0 0 0;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e1e5e9;
            border-radius: 5px;
            font-size: 1rem;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .login-button {
            width: 100%;
            padding: 0.75rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .login-button:hover {
            transform: translateY(-2px);
        }
        .error-message {
            background: #fee;
            color: #c33;
            padding: 0.75rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            border: 1px solid #fcc;
        }
        .success-message {
            background: #efe;
            color: #363;
            padding: 0.75rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            border: 1px solid #cfc;
        }
        .admin-info {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin-top: 1rem;
            font-size: 0.9rem;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>🔐 Admin Login</h1>
            <p>GrampsWeb Social Network</p>
        </div>
        
        {% if error %}
        <div class="error-message">{{ error }}</div>
        {% endif %}
        
        {% if success %}
        <div class="success-message">{{ success }}</div>
        {% endif %}
        
        <form method="POST" action="/adm">
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required value="{{ email or 'admin@ozimiz.org' }}">
            </div>
            
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="login-button">Login as Admin</button>
        </form>
        
        <div class="admin-info">
            <strong>Default Admin:</strong><br>
            Email: admin@ozimiz.org<br>
            Password: admin123
        </div>
    </div>
</body>
</html>
"""

@admin_auth_bp.route('/adm', methods=['GET', 'POST'])
def admin_login():
    """Admin login page and authentication"""
    if request.method == 'GET':
        return render_template_string(ADMIN_LOGIN_TEMPLATE)
    
    # Handle POST request
    try:
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            return render_template_string(ADMIN_LOGIN_TEMPLATE, 
                                        error="Email and password are required", 
                                        email=email)
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return render_template_string(ADMIN_LOGIN_TEMPLATE, 
                                        error="Invalid credentials", 
                                        email=email)
        
        # Check password
        if not user.check_password(password):
            return render_template_string(ADMIN_LOGIN_TEMPLATE, 
                                        error="Invalid credentials", 
                                        email=email)
        
        # Check if user is admin
        if not user.can_admin():
            return render_template_string(ADMIN_LOGIN_TEMPLATE, 
                                        error="Access denied. Admin privileges required.", 
                                        email=email)
        
        # Check if user is active
        if user.status.value != 'active':
            return render_template_string(ADMIN_LOGIN_TEMPLATE, 
                                        error="Account is not active", 
                                        email=email)
        
        # Generate tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Return success with tokens
        success_message = f"""
        <h3>✅ Login Successful!</h3>
        <p><strong>Welcome, {user.display_name or user.username}!</strong></p>
        <p><strong>Role:</strong> {user.role.value}</p>
        <p><strong>Access Token:</strong></p>
        <textarea readonly style="width: 100%; height: 100px; font-family: monospace; font-size: 0.8rem;">{access_token}</textarea>
        <p><strong>Refresh Token:</strong></p>
        <textarea readonly style="width: 100%; height: 100px; font-family: monospace; font-size: 0.8rem;">{refresh_token}</textarea>
        <p><strong>API Endpoints:</strong></p>
        <ul>
            <li><a href="/api/admin/users" target="_blank">/api/admin/users</a> - Manage users</li>
            <li><a href="/api/admin/posts" target="_blank">/api/admin/posts</a> - Manage posts</li>
            <li><a href="/api/feed/popular" target="_blank">/api/feed/popular</a> - Popular feed</li>
            <li><a href="/api/ai/status" target="_blank">/api/ai/status</a> - AI status</li>
        </ul>
        <p><em>Use the Access Token in Authorization header: "Bearer {access_token[:50]}..."</em></p>
        """
        
        return render_template_string(ADMIN_LOGIN_TEMPLATE, success=success_message, email=email)
        
    except Exception as e:
        logger.error(f"Error in admin login: {str(e)}")
        return render_template_string(ADMIN_LOGIN_TEMPLATE, 
                                    error=f"Internal server error: {str(e)}", 
                                    email=request.form.get('email', ''))

@admin_auth_bp.route('/adm/api/login', methods=['POST'])
def admin_api_login():
    """Admin login API endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is admin
        if not user.can_admin():
            return jsonify({'error': 'Admin privileges required'}), 403
        
        # Check if user is active
        if user.status.value != 'active':
            return jsonify({'error': 'Account is not active'}), 401
        
        # Generate tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in admin API login: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

