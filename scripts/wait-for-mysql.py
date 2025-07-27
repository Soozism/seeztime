#!/usr/bin/env python3
"""
Wait for MySQL to be ready before starting the application
"""

import time
import sys
import os
import mysql.connector
from mysql.connector import Error

def wait_for_mysql(host, port, user, password, database, max_attempts=30):
    """Wait for MySQL to be ready"""
    print(f"Waiting for MySQL at {host}:{port}...")
    
    for attempt in range(max_attempts):
        try:
            # Try to connect to MySQL
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            
            if connection.is_connected():
                print("✅ MySQL is ready!")
                connection.close()
                return True
                
        except Error as e:
            print(f"Attempt {attempt + 1}/{max_attempts}: MySQL not ready yet... ({e})")
            time.sleep(2)
    
    print("❌ MySQL failed to start within the expected time")
    return False

if __name__ == "__main__":
    # Get MySQL connection details from environment
    host = os.getenv("MYSQL_HOST", "mysql")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "gingatek")
    password = os.getenv("MYSQL_PASSWORD", "gingatek123")
    database = os.getenv("MYSQL_DATABASE", "ginga_tek")
    
    if not wait_for_mysql(host, port, user, password, database):
        sys.exit(1) 