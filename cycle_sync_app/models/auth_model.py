import sqlite3
from models.data_manager.database_manager import DatabaseManager

class AuthModel:
    def __init__(self):
        DatabaseManager.initialize_database()
        
    def register_account(self, username, password, role):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO accounts (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', (username, password, role))
            conn.commit()
            account_id = cursor.lastrowid
            return account_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
            
    def mock_cached_login(self, role: str):
        """Returns a hardcoded user profile for quick Hackathon judging."""
        # --- FIX: Update the roles to match the new Unipol pivot ---
        if role == "DRIVER":
            return self.get_account_by_username("mario_driver")
        elif role == "INSURER":  # <--- Changed from OEM to INSURER
            return self.get_account_by_username("maserati_oem") # We can keep the old username for now so it loads the existing DB data!
        return None

    def get_account_by_username(self, username):
        """Fetches an account by username."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username FROM accounts 
            WHERE username = ? LIMIT 1
        ''', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {'account_id': result[0], 'username': result[1]}
        return None
