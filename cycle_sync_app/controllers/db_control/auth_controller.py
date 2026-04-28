from PyQt6.QtCore import QObject, pyqtSignal

class AuthController(QObject):
    auth_successful = pyqtSignal(dict)
    
    def __init__(self, view, model):
        super().__init__()
        self.view = view
        self.model = model
        self.current_role = None
        
        self.view.login_requested.connect(self.handle_login_request)
        
    def handle_login_request(self, username, password):
        if not self.current_role:
            return
            
        account_id = None
        
        if username:
            # Try to register
            account_id = self.model.register_account(username, password or 'hash', self.current_role)
            if account_id is None:
                # If already exists, fetch it
                acc = self.model.get_account_by_username(username)
                if acc:
                    account_id = acc['account_id']
                else:
                    print(f"[Auth] Could not register or find account: {username}")
                    return
        else:
            # Fallback to mock cached login for judges
            acc = self.model.mock_cached_login(self.current_role)
            if acc:
                account_id = acc['account_id']
                username = acc['username']
            else:
                print(f"[Auth] No cached profile found for role: {self.current_role}")
                return

        self.auth_successful.emit({
            'role': self.current_role,
            'account_id': account_id,
            'username': username
        })

    
