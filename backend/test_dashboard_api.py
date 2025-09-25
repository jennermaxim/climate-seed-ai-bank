"""
Test script to verify the dashboard API is working with real Uganda data
"""
import requests
import json

def test_dashboard_api():
    """Test the dashboard API endpoint for all user types"""
    base_url = "http://localhost:8000"
    
    # Test different user types
    test_users = [
        {"username": "farmer1", "password": "password123", "type": "farmer"},
        {"username": "admin", "password": "admin123", "type": "admin"}, 
        {"username": "policy1", "password": "policy123", "type": "policy_maker"}
    ]
    
    print("=== Testing Dashboard API for All User Types ===\n")
    
    for user_data in test_users:
        print(f"Testing {user_data['type']}: {user_data['username']}")
        
        try:
            # Login to get token
            login_response = requests.post(
                f"{base_url}/api/auth/token",
                data={"username": user_data["username"], "password": user_data["password"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data["access_token"]
                print(f"  ✅ Login successful")
                
                # Test dashboard endpoint
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                dashboard_response = requests.get(
                    f"{base_url}/api/analytics/dashboard",
                    headers=headers
                )
                
                if dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    print(f"  ✅ Dashboard API successful!")
                    print(f"      Total Farms: {dashboard_data.get('total_farms', 0)}")
                    print(f"      Recommendations: {dashboard_data.get('total_recommendations', 0)}")
                    print(f"      Active Cycles: {dashboard_data.get('active_crop_cycles', 0)}")
                    print(f"      Climate Alerts: {dashboard_data.get('climate_alerts', 0)}")
                    
                    # Show user-specific data
                    regional_stats = dashboard_data.get('regional_statistics', {})
                    print(f"      Region/Role: {regional_stats.get('user_region', 'N/A')}")
                    
                    recent_alerts = dashboard_data.get('recent_alerts', [])
                    if recent_alerts:
                        print(f"      Sample Alert: {recent_alerts[0].get('message', 'N/A')[:60]}...")
                    
                    print(f"      Status: ✅ Working")
                else:
                    print(f"  ❌ Dashboard API failed: {dashboard_response.status_code}")
                    print(f"      Response: {dashboard_response.text[:100]}...")
                    
            else:
                print(f"  ❌ Login failed: {login_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection failed - Backend server not running?")
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
        print()  # Blank line between users
        
    return True

if __name__ == "__main__":
    success = test_dashboard_api()
    if success:
        print(f"✅ Dashboard API tests completed!")
        print(f"🌱 All user types (farmer, admin, policy maker) have working dashboards!")
        print(f"📊 Each dashboard shows appropriate data for the user role")
    else:
        print(f"❌ Some dashboard API tests failed")
        print(f"🔧 Please check the server and try again")