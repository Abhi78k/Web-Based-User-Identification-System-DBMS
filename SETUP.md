# Quick Setup Guide

## Prerequisites

1. **Python 3.8+** installed on your system
2. **MySQL** server running
3. **pip** (Python package manager)

## Step-by-Step Setup

### 1. Install Python Dependencies

Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- Flask
- Flask-Login
- PyMySQL
- Werkzeug
- python-dotenv
- Pillow

### 2. Configure MySQL Database

#### Option A: Automatic Setup (Recommended)
The application will automatically create the database and tables when you run it for the first time.

#### Option B: Manual Setup
Run the provided SQL script:

```bash
mysql -u root -p < init_database.sql
```

Or import it through a MySQL client (phpMyAdmin, MySQL Workbench, etc.)

### 3. Configure Environment Variables

Create a `.env` file in the root directory with your MySQL credentials:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=secure_auth
SECRET_KEY=your-secret-key-change-this-in-production
```

**Important:** Replace `your_mysql_password` with your actual MySQL password and change the SECRET_KEY to a random string for production.

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 5. Access the Application

1. Open your browser and go to `http://localhost:5000`
2. Click "Register" to create your first account
3. After registration, log in with your credentials
4. For admin access, you can manually update the role in the database or register the first user and change their role to Admin

## First Admin User Setup

To create the first admin user:

1. Register a regular user through the web interface
2. In MySQL, run:
```sql
USE secure_auth;
UPDATE Users SET role_id = 1 WHERE username = 'your_username';
```
(Replace `your_username` with the username you registered)

Or register through the web interface and use a database client to change the role_id to 1 (Admin role).

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution:** Run `pip install -r requirements.txt`

### Issue: "Can't connect to MySQL server"
**Solution:** 
1. Verify MySQL is running
2. Check credentials in `.env` file
3. Ensure MySQL server is accessible

### Issue: "Access denied for user"
**Solution:** Check your MySQL username and password in the `.env` file

### Issue: Database tables not created
**Solution:** Run the `init_database.sql` script manually or check MySQL user permissions

## Testing the Application

1. **Register a user**: Go to `/register` and create an account
2. **Login**: Use your credentials to log in
3. **View Dashboard**: See your profile information and session history
4. **Edit Profile**: Update your information and upload a profile picture
5. **Admin Panel**: If you're an admin, access `/admin/dashboard` to see system statistics

## Default Routes

- `/` - Home/Login page
- `/register` - User registration
- `/login` - User login
- `/dashboard` - User dashboard
- `/profile` - Edit profile
- `/admin/dashboard` - Admin panel (Admin only)
- `/admin/users` - User management (Admin only)
- `/admin/logs` - System logs (Admin only)
- `/logout` - Logout

## Security Notes

1. **Never commit the `.env` file** to version control (it's in `.gitignore`)
2. **Change the SECRET_KEY** in production
3. **Use strong passwords** for MySQL
4. **Enable HTTPS** in production
5. **Regular backups** of the database

## Next Steps

- Review the `README.md` for detailed documentation
- Customize the UI in `templates/` and `static/css/`
- Add additional features as needed
- Deploy to a production server when ready

