#!/usr/bin/env python3
"""
Create admin user script using raw SQL to avoid circular imports
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.auth import get_password_hash
from app.models.enums import UserRole

def create_admin_user():
    """Create admin user directly using SQL"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Check if admin user already exists
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
            if result.fetchone():
                print("✅ Admin user already exists!")
                return
            
            # Create admin user
            password_hash = get_password_hash("admin123")
            conn.execute(text("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active)
                VALUES (:username, :email, :password_hash, :first_name, :last_name, :role, :is_active)
            """), {
                "username": "admin",
                "email": "admin@gingatek.com",
                "password_hash": password_hash,
                "first_name": "Admin",
                "last_name": "User",
                "role": UserRole.ADMIN.value,
                "is_active": True
            })
            conn.commit()
            
        print("✅ Admin user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@gingatek.com")
        print("⚠️  Please change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin_user()
