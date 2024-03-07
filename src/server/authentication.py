# Authentication server
import sqlite3
import hashlib

class Authentication():

    '''
    Init function for Authentication
    '''
    def __init__(self) -> None:
        try:
            self.conn = sqlite3.connect('users.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
            self.conn.commit()
        except Exception as e:
            print(f"ERROR: {e}")

    '''
    Register the user to database

    self: Authentication
    username: string of the username
    password: hashed password
    '''
    def register_user(self, username, password):
        hashed_pass = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute('''INSERT INTO users VALUES (?, ?)''', (username, hashed_pass))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            return False # if the user already in the database
        return True

    '''
    Check the user from database

    self: Authentication
    username: string of the username
    password: hashed password
    '''
    def authenticate_user(self, username, password):
        hashed_pass = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute('''SELECT * FROM users WHERE username=? AND password=?''', (username, hashed_pass))
        return self.cursor.fetchone() is not None
    
    '''
    Closing the database

    self: Authentication
    '''
    def close_database(self):
        self.conn.close()
