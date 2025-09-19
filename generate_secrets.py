#!/usr/bin/env python3
"""
Script to generate secure secrets for the social network application.
Run this script to generate a .env file with secure random values.
"""

import secrets
import string
import os

def generate_secret_key(length=32):
    """Generate a secure random secret key."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_password(length=16):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔐 Generating secure secrets for Social Network...")
    
    # Generate secrets
    secret_key = generate_secret_key(64)
    jwt_secret = generate_secret_key(64)
    postgres_password = generate_password(20)
    
    # Create .env content
    env_content = f"""# Backend Configuration
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Database Configuration
POSTGRES_DB=social_network
POSTGRES_USER=postgres
POSTGRES_PASSWORD={postgres_password}

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration (Optional)
MAIL_SERVER=mail.ozimiz.org
MAIL_PORT=465
MAIL_USE_SSL=true
MAIL_USERNAME=noreply@ozimiz.org
MAIL_PASSWORD=your_email_password_here
MAIL_DEFAULT_SENDER=noreply@ozimiz.org

# Frontend Configuration
VITE_API_URL=https://my.ozimiz.org/api

# Domain and SSL Configuration
DOMAIN=my.ozimiz.org
CERTBOT_EMAIL=your-email@example.com
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Generated .env file with secure secrets!")
    print("🔑 Generated secrets:")
    print(f"   SECRET_KEY: {secret_key[:20]}...")
    print(f"   JWT_SECRET_KEY: {jwt_secret[:20]}...")
    print(f"   POSTGRES_PASSWORD: {postgres_password}")
    print("\n⚠️  IMPORTANT: Update the email settings in .env file!")
    print("📧 Set MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER, and CERTBOT_EMAIL")

if __name__ == "__main__":
    main()
