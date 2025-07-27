-- MySQL initialization script for Ginga Tek
-- This script runs when the MySQL container starts for the first time

-- Set character set and collation
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;

-- Create database if it doesn't exist (should already exist from environment variables)
-- CREATE DATABASE IF NOT EXISTS ginga_tek CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE ginga_tek;

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON ginga_tek.* TO 'gingatek'@'%';
FLUSH PRIVILEGES; 