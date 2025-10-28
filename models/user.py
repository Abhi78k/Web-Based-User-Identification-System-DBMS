from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, username, email, password, full_name=None, profile_pic=None, role_id=None, created_at=None, updated_at=None):
        self.id = user_id
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.full_name = full_name
        self.profile_pic = profile_pic
        self.role_id = role_id
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'profile_pic': self.profile_pic,
            'role_id': self.role_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

