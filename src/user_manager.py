class UserManager:
    def __init__(self,users):
        self.users = users
        self.current_user = None

    def register(self,username,pasword):
        username = username.lower().strip()
        if username in self.users:
            message = "Username already exists"
            return False , message
        elif username.isalnum():
            if len(pasword) >= 8 :
                if username == "admin":
                    self.users[username] = {"password" : pasword , "is_admin" : True }
                    message = "Account is added please login!"
                    return True,message
                else:
                    self.users[username] = {"password" : pasword , "is_admin" : False }
                    message = "Account is added please login!"
                    return True,message
            else:
                message = "Password must be at least 8 characters long"
                return False,message
        else:
            message = "Please provide a valid username that contin only letter or albhabects"
            return False,message

    def login(self,username,password):
        username = username.lower().strip()
        password = password.strip()
        if username in self.users:
            if self.users[username]["password"] == password:
                self.current_user = username
                message = f"Welcome {username}!"
                return True,message
            else:
                message = "Incorrect password"
                return False,message
        else:
            message = "Username does not exist"
            return False,message
        
    def logout(self):
        if self.current_user:
            self.current_user = None

    def is_authenticated(self):
        return self.current_user is not None
    
    def is_admin(self):
        if self.current_user and self.users[self.current_user]["is_admin"]:
            return True
        else:
            return False

    def set_role(self,username,is_admin=False):
        if self.is_admin():
            username = username.lower().strip()
            if username in self.users:
                self.users[username]["is_admin"] = is_admin
                status = "Admin" if is_admin else "Not Admin"
                message = f"{username} is now {status}"
                return True,message
            else:
                message = "Username does not exist"
                return False,message
        else:
            message = "You do not have permission to perform this action"
            return False,message
        
    def forgot_password(self,username,char,position,new_password,confirm_password):
        if username not in self.users:
            message = "Username does not exist"  
            return False,message
        else:
            if position == "first" and not self.users[username]["password"].startswith(char):
                message = "Incorrect first characters"
                return False,message
            elif position == "last" and not self.users[username]["password"].endswith(char):
                message = "Incorrect last characters"
                return False,message
            else:
                if new_password == self.users[username]["password"]:
                    message = "Can not set the old password as new password"
                    return False,message
                else:
                    if len(new_password) >= 8 :
                        if new_password != confirm_password:
                            message = "New password and confirm password do not match"
                            return False,message
                        self.users[username]["password"] = new_password
                        message = "Password is successfully changed"
                        return True,message
                    else:
                        message = "Password must be at least 8 characters long"
                        return False,message
                    

        


