class Session:
    def __init__(self, session_id, user_id, login_time, logout_time=None, ip_address=None, user_agent=None):
        self.session_id = session_id
        self.user_id = user_id
        self.login_time = login_time
        self.logout_time = logout_time
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'login_time': self.login_time,
            'logout_time': self.logout_time,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }

