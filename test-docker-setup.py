#!/usr/bin/env python3
"""
Test script to verify Docker setup for Ginga Tek
"""

import subprocess
import sys
import time
import requests

def run_command(command, check=True):
    """Run a shell command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Command failed: {command}")
            print(f"Error: {result.stderr}")
            return False
        return result
    except Exception as e:
        print(f"❌ Error running command '{command}': {e}")
        return False

def check_docker():
    """Check if Docker is available"""
    print("🔍 Checking Docker...")
    result = run_command("docker --version")
    if result:
        print(f"✅ Docker is available: {result.stdout.strip()}")
        return True
    return False

def check_docker_compose():
    """Check if Docker Compose is available"""
    print("🔍 Checking Docker Compose...")
    result = run_command("docker compose version")
    if result:
        print(f"✅ Docker Compose is available: {result.stdout.strip()}")
        return True
    return False

def check_ports():
    """Check if required ports are available"""
    print("🔍 Checking port availability...")
    
    import socket
    
    ports = [8000, 3306]
    available = True
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            print(f"✅ Port {port} is available")
        except OSError:
            print(f"⚠️  Port {port} is already in use")
            available = False
    
    return available

def test_docker_build():
    """Test Docker build"""
    print("🔨 Testing Docker build...")
    result = run_command("docker compose build --no-cache")
    if result:
        print("✅ Docker build successful")
        return True
    return False

def test_docker_run():
    """Test Docker run"""
    print("🚀 Testing Docker run...")
    
    # Start services
    result = run_command("docker compose up -d")
    if not result:
        return False
    
    # Wait for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(20)
    
    # Check if services are running
    result = run_command("docker compose ps")
    if result:
        print("✅ Services are running")
        print(result.stdout)
    
    # Test API
    print("🌐 Testing API...")
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("✅ API is responding")
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API is not responding: {e}")
        return False
    
    # Stop services
    print("🛑 Stopping services...")
    run_command("docker compose down", check=False)
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Ginga Tek Docker Setup")
    print("=" * 50)
    
    tests = [
        ("Docker", check_docker),
        ("Docker Compose", check_docker_compose),
        ("Port Availability", check_ports),
        ("Docker Build", test_docker_build),
        ("Docker Run", test_docker_run)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n📋 Testing {name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Docker setup is ready.")
        print("\n🚀 To start development:")
        print("   ./start-dev.sh")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 