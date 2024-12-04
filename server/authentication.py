from typing import Dict
import json

class AuthenticationManager:
    def __init__(self):
        self.filename = "users.json"
        self.users: Dict[str, str] = self.load_from_file()

    def register_user(self, username: str, password: str):
        if username in self.users:
            raise ValueError(f"User {username} already exists")
        self.users[username] = password

    def authenticate(self, username: str, password: str) -> bool:
        if username not in self.users:
            return False
        return self.users[username] == password
    
    def load_from_file(self) -> Dict[str, str]:
        try:
            with open(self.filename, "r") as file:
                users = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            users = {}
        
        return users
    
    def save_to_file(self):
        try:
            with open(self.filename, "w") as file:
                json.dump(self.users, file)
        except FileNotFoundError:
            print(f"Error: file {self.filename} not found")
        except json.JSONDecodeError:
            print(f"Error: failed to save data to {self.filename}")
        

    

