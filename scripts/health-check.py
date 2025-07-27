#!/usr/bin/env python3
"""
Health check script for Ginga Tek Docker environment
"""

import requests
import mysql.connector
import sys
import os
from mysql.connector import Error

def check_api():
    """Check if the API is responding"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ API is responding")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API is not responding: {e}")
        return False

def check_api_docs():
    """Check if API documentation is available"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API documentation is available")
            return True
        else:
            print(f"❌ API docs returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API docs not available: {e}")
        return False

def check_mysql():
    """Check if MySQL is accessible"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="gingatek",
            password="gingatek123",
            database="ginga_tek"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ MySQL is accessible (Version: {version[0]})")
            cursor.close()
            connection.close()
            return True
        else:
            print("❌ MySQL connection failed")
            return False
            
    except Error as e:
        print(f"❌ MySQL is not accessible: {e}")
        return False

def check_admin_user():
    """Check if admin user exists"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="gingatek",
            password="gingatek123",
            database="ginga_tek"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT username, email, role FROM users WHERE username = 'admin'")
            user = cursor.fetchone()
            
            if user:
                print(f"✅ Admin user exists: {user[0]} ({user[1]}) - Role: {user[2]}")
                cursor.close()
                connection.close()
                return True
            else:
                print("❌ Admin user not found")
                cursor.close()
                connection.close()
                return False
                
    except Error as e:
        print(f"❌ Could not check admin user: {e}")
        return False

def main():
    """Run all health checks"""
    print("🔍 Running Ginga Tek Health Checks...")
    print("=" * 50)
    
    checks = [
        ("API", check_api),
        ("API Documentation", check_api_docs),
        ("MySQL Database", check_mysql),
        ("Admin User", check_admin_user)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        if check_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Health Check Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All services are healthy!")
        print("\n🌐 Access your application:")
        print("   API: http://localhost:8000")
        print("   Docs: http://localhost:8000/docs")
        print("   Admin: admin / admin123")
    else:
        print("⚠️  Some services are not healthy. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 