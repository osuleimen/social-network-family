#!/usr/bin/env python3
"""
Script to create SuperAdmin user for the social network.
This script should be run only once during initial setup.
"""

import os
import sys
import getpass
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, UserRole, AuditLog

def create_superadmin():
    """Create SuperAdmin user"""
    app = create_app()
    
    with app.app_context():
        # Check if SuperAdmin already exists
        superadmin_count = User.get_superadmin_count()
        if superadmin_count > 0:
            print("SuperAdmin already exists. Skipping creation.")
            return
        
        print("Creating SuperAdmin user...")
        print("This is a one-time setup process.")
        print()
        
        # Get SuperAdmin details
        print("Enter SuperAdmin details:")
        identifier = input("Phone number or email: ").strip()
        if not identifier:
            print("Error: Identifier is required")
            return
        
        # Determine identifier type
        if '@' in identifier:
            identifier_type = 'email'
        else:
            identifier_type = 'phone'
        
        # Get additional details
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        display_name = input("Display name (optional): ").strip()
        username = input("Username (optional): ").strip()
        
        # Create SuperAdmin user
        try:
            superadmin = User.create_superadmin(
                identifier=identifier,
                user_type=identifier_type,
                first_name=first_name,
                last_name=last_name,
                display_name=display_name or f"{first_name} {last_name}".strip(),
                username=username.lower() if username else None
            )
            
            # Generate profile slug if username is provided
            if username:
                superadmin.profile_slug = superadmin.generate_profile_slug(username)
            
            db.session.add(superadmin)
            db.session.commit()
            
            # Log the creation in audit log
            AuditLog.log_action(
                actor_id=superadmin.id,
                action="create_superadmin",
                target_type="user",
                target_id=superadmin.id,
                action_metadata={
                    "created_by": "system",
                    "setup_script": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            db.session.commit()
            
            print()
            print("✅ SuperAdmin created successfully!")
            print(f"User ID: {superadmin.id}")
            print(f"Identifier: {superadmin.identifier}")
            print(f"Role: {superadmin.role.value}")
            print(f"Username: {superadmin.username or 'Not set'}")
            print(f"Profile slug: {superadmin.profile_slug or 'Not set'}")
            print()
            print("⚠️  Important: SuperAdmin has full access to the system.")
            print("   Keep the credentials secure and use responsibly.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating SuperAdmin: {str(e)}")
            return

def main():
    """Main function"""
    print("=" * 60)
    print("Social Network - SuperAdmin Creation Script")
    print("=" * 60)
    print()
    
    # Confirm this is intentional
    print("⚠️  WARNING: This script creates a SuperAdmin user with full system access.")
    print("   Only run this script during initial system setup.")
    print()
    
    confirm = input("Are you sure you want to create a SuperAdmin? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Operation cancelled.")
        return
    
    create_superadmin()

if __name__ == "__main__":
    main()
