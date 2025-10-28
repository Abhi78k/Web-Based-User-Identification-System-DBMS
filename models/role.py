class Role:
    def __init__(self, role_id, role_name, description=None):
        self.role_id = role_id
        self.role_name = role_name
        self.description = description
    
    def to_dict(self):
        return {
            'role_id': self.role_id,
            'role_name': self.role_name,
            'description': self.description
        }

