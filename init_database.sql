-- Database initialization script for Secure Auth System
-- Run this script to manually set up the database if needed

-- Create database
CREATE DATABASE IF NOT EXISTS secure_auth;
USE secure_auth;

-- Create Roles table
CREATE TABLE IF NOT EXISTS Roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);

-- Insert default roles
INSERT INTO Roles (role_name, description) VALUES ('Admin', 'Administrator with full access')
ON DUPLICATE KEY UPDATE role_name=role_name;
INSERT INTO Roles (role_name, description) VALUES ('User', 'Regular user with limited access')
ON DUPLICATE KEY UPDATE role_name=role_name;

-- Create Users table
CREATE TABLE IF NOT EXISTS Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    profile_pic VARCHAR(255),
    role_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES Roles(role_id)
);

-- Create Sessions table
CREATE TABLE IF NOT EXISTS Sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Create AuditLogs table
CREATE TABLE IF NOT EXISTS AuditLogs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100),
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Optional: Create an admin user
-- Password hash for "admin123" (change this in production!)
-- INSERT INTO Users (username, email, hashed_password, full_name, role_id) 
-- VALUES ('admin', 'admin@example.com', 'pbkdf2:sha256:600000$...', 'Admin User', 1)
-- ON DUPLICATE KEY UPDATE username=username;

