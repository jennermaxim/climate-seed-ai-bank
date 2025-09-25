#!/usr/bin/env python3
"""
Script to create test users for the Climate-Adaptive Seed AI Bank
"""
import sys
from models import SessionLocal
from models.database_models import User
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_users():
    """Create test users for testing the application"""
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Found {existing_users} existing users in database")
            users = db.query(User).all()
            for user in users:
                print(f"- {user.username} ({user.user_type})")
            return
        
        # Create test users
        test_users = [
            {
                "username": "farmer1",
                "email": "farmer1@example.com",
                "full_name": "John Mugisha",
                "password_hash": pwd_context.hash("password123"),
                "user_type": "farmer",
                "is_active": True
            },
            {
                "username": "admin",
                "email": "admin@example.com", 
                "full_name": "Admin User",
                "password_hash": pwd_context.hash("admin123"),
                "user_type": "admin",
                "is_active": True
            },
            {
                "username": "policy1",
                "email": "policy1@example.com",
                "full_name": "Policy Maker",
                "password_hash": pwd_context.hash("policy123"),
                "user_type": "policy_maker",
                "is_active": True
            }
        ]
        
        for user_data in test_users:
            user = User(**user_data)
            db.add(user)
            print(f"Created user: {user_data['username']} (password: {user_data['password_hash'][:20]}...)")
        
        db.commit()
        print("\n✅ Test users created successfully!")
        print("\n📋 Login credentials:")
        print("👨‍🌾 Farmer: farmer1 / password123")
        print("👨‍💼 Admin: admin / admin123") 
        print("🏛️ Policy Maker: policy1 / policy123")
        
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()