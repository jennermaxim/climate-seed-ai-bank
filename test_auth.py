#!/usr/bin/env python3
"""
Test script to verify authentication fixes work correctly
"""
import requests
import json

# Test user data
test_user = {
    "username": "testuser",
    "email": "test@example.com", 
    "full_name": "Test User",
    "password": "testpassword",
    "user_type": "farmer",
    "phone_number": "+256700000000",
    "location": "Kampala"
}

login_data = {
    "username": "test@example.com",  # Using email as username
    "password": "testpassword"
}

base_url = "http://localhost:8000"

def test_authentication():
    print("Testing authentication flow...")
    
    # 1. Register user
    print("\n1. Registering test user...")
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=test_user)
        if response.status_code == 200:
            print("✅ User registration successful")
        elif response.status_code == 400:
            print("ℹ️  User already exists (expected if running multiple times)")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except requests.ConnectionError:
        print("❌ Cannot connect to backend server. Please start it with:")
        print("cd /media/jennermaxim/5CFF4F940243C13D1/projects/hackathon/climate-seed-ai-bank/backend")
        print("python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return False
    
    # 2. Login
    print("\n2. Testing login with email as username...")
    try:
        response = requests.post(f"{base_url}/api/auth/login", 
                               data=login_data,
                               headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful")
            print(f"Token type: {token_data['token_type']}")
            access_token = token_data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # 3. Test authenticated endpoint
    print("\n3. Testing authenticated API call...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{base_url}/api/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Authenticated API call successful")
            print(f"User: {user_data['full_name']} ({user_data['email']})")
        else:
            print(f"❌ Authenticated API call failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Authenticated API call error: {e}")
        return False
    
    # 4. Test farms endpoint
    print("\n4. Testing farms endpoint...")
    try:
        response = requests.get(f"{base_url}/api/farms/", headers=headers)
        
        if response.status_code == 200:
            farms = response.json()
            print(f"✅ Farms API call successful - returned {len(farms)} farms")
        else:
            print(f"❌ Farms API call failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Farms API call error: {e}")
        return False
    
    print("\n🎉 All authentication tests passed!")
    return True

if __name__ == "__main__":
    test_authentication()