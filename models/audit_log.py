class AuditLog:
    def __init__(self, log_id, user_id, action, action_time):
        self.log_id = log_id
        self.user_id = user_id
        self.action = action
        self.action_time = action_time
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'action': self.action,
            'action_time': self.action_time
        }

