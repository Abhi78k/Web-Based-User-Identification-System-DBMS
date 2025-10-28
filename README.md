# Secure Web-Based User Identification System

A complete, production-ready web application built with Flask (Python) and MySQL that provides secure user authentication, role-based access control, session tracking, and comprehensive audit logging.

## Features

- **Secure Authentication**: Registration and login with password hashing using Werkzeug
- **Role-Based Access Control**: Admin and User roles with appropriate permissions
- **Session Management**: Tracks user login/logout times, IP addresses, and user agents
- **Audit Logging**: Comprehensive logging of all user actions
- **Profile Management**: Users can update their profile information and upload profile pictures
- **Admin Panel**: Full user management interface for administrators
- **Responsive UI**: Clean, modern interface using Bootstrap 5

## Project Structure

```
secure_auth_system/
│
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # This file
│
├── models/              # Data models
│   ├── __init__.py
│   ├── user.py
│   ├── role.py
│   ├── session.py
│   └── audit_log.py
│
├── routes/              # Application routes (blueprints)
│   ├── __init__.py
│   ├── auth.py         # Authentication routes
│   ├── admin.py        # Admin panel routes
│   └── dashboard.py    # User dashboard routes
│
├── utils/               # Utility modules
│   ├── __init__.py
│   ├── security.py     # Password hashing and validation
│   ├── logging.py      # Audit log management
│   └── sessions.py     # Session management
│
├── static/              # Static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── uploads/        # Profile pictures (created automatically)
│
└── templates/          # HTML templates
    ├── base.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── profile.html
    ├── admin_dashboard.html
    ├── admin_users.html
    └── admin_logs.html
```

## Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd secure_auth_system
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MySQL:**
   - Create a new MySQL database named `secure_auth` (or your preferred name)
   - Update the `.env` file with your MySQL credentials:
     ```
     DB_HOST=localhost
     DB_USER=root
     DB_PASSWORD=yourpassword
     DB_NAME=secure_auth
     SECRET_KEY=your-secret-key-change-this-in-production
     ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## Database Schema

The application automatically creates the following tables on first run:

### Users Table
- Stores user credentials and profile information
- Passwords are hashed using Werkzeug's secure hashing
- Links to Roles table via foreign key

### Roles Table
- Defines user roles (Admin, User)
- Created with default roles on initialization

### Sessions Table
- Tracks user login and logout activities
- Records IP addresses and user agents
- Links to Users table via foreign key

### AuditLogs Table
- Logs all important user actions
- Includes timestamps for audit trail
- Links to Users table via foreign key

## Usage

### User Registration
1. Navigate to the registration page
2. Enter username, email, and password
3. Password must be at least 8 characters with uppercase, lowercase, and a number
4. Click "Register" to create your account

### User Login
1. Navigate to the login page
2. Enter your username and password
3. Click "Login" to access your account
4. You'll be redirected to the dashboard (or admin panel if you're an admin)

### Profile Management
1. Go to your dashboard
2. Click "Profile" in the navigation bar
3. Update your full name
4. Upload a profile picture (optional)
5. Click "Update Profile" to save changes

### Admin Functions
Admin users have access to additional features:
- **Admin Dashboard**: View system statistics
- **User Management**: View, edit, and delete users
- **System Logs**: View audit logs and session history

### Account Deletion
Users can delete their accounts from the profile page. This action is irreversible.

## Security Features

- **Password Hashing**: Uses Werkzeug's secure password hashing (PBKDF2)
- **Session Management**: Secure session handling with Flask-Login
- **Role-Based Access**: Decorators to enforce role-based permissions
- **SQL Injection Prevention**: Uses parameterized queries
- **File Upload Validation**: Checks file types and sizes
- **CSRF Protection**: Enabled by default in Flask

## Troubleshooting

### Database Connection Error
- Verify MySQL is running
- Check credentials in `.env` file
- Ensure the database exists

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're in the correct directory

### Upload Folder Issues
- The application creates the `static/uploads` folder automatically
- Ensure the application has write permissions for this folder

## Development

To run in development mode with auto-reload:
```bash
python app.py
```

The app will run on `http://localhost:5000` with debug mode enabled.

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL with PyMySQL
- **Authentication**: Flask-Login
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Security**: Werkzeug password hashing


