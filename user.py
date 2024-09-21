import shelve
from flask_login import UserMixin
class User(UserMixin):
    def __init__(self, username, email, password, name='', age='', street_name='', unit_number='', country=''):
        self.__username = username
        self.__email = email
        self.__password = password
        self.__name = name
        self.__age = age
        self.__street_name = street_name
        self.__unit_number = unit_number
        self.__country = country
        self.__points = 0
        self.__redeemed_rewards = []

    def redeem_reward(self, reward):
        self.__redeemed_rewards.append(reward)
        User.save_to_shelve(self)
        return True

    def delete_redeemed_reward(self, reward_id):
        print(f"Deleting redeemed reward with ID: {reward_id}")
        for redeemed_reward in self.__redeemed_rewards:
            if redeemed_reward.get_id() == reward_id:
                print(f"Found matching reward. Deleting: {redeemed_reward.get_name()}")
                self.__redeemed_rewards.remove(redeemed_reward)
                return True  # Successfully deleted
        print(f"No matching reward found with ID: {reward_id}")
        return False

    def get_redeemed_rewards(self):
        return self.__redeemed_rewards

    def get_username(self):
        return self.__username

    def set_username(self, username):
        self.__username = username

    def get_email(self):
        return self.__email

    def set_email(self, email):
        self.__email = email

    def get_password(self):
        return self.__password

    def set_password(self, password):
        self.__password = password

    def check_password(self, password):
        return self.__password == password

    def get_id(self):
        return self.get_username()

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_age(self):
        return self.__age

    def set_age(self, age):
        self.__age = age

    def get_street_name(self):
        return self.__street_name

    def set_street_name(self, street_name):
        self.__street_name = street_name

    def get_unit_number(self):
        return self.__unit_number

    def set_unit_number(self, unit_number):
        self.__unit_number = unit_number

    def get_country(self):
        return self.__country

    def set_country(self, country):
        self.__country = country

    def get_points(self):
        return self.__points

    def set_points(self, points):
        self.__points = points


    def get_particulars(self):
        return {
            'name': self.__name,
            'age': self.__age,
            'street_name': self.__street_name,
            'unit_number': self.__unit_number,
            'country': self.__country
        }

    def update_particulars(self, name=None, age=None, street_name=None, unit_number=None, country=None):
        if name is not None:
            self.__name = name
        if age is not None:
            self.__age = age
        if street_name is not None:
            self.__street_name = street_name
        if unit_number is not None:
            self.__unit_number = unit_number
        if country is not None:
            self.__country = country

    @staticmethod
    def save_to_shelve(user):
        with shelve.open("user_db.shelve", writeback=True) as db:
            username = user.get_username()

            # Check if the user already exists in the shelve file
            if username in db:
                existing_user = db[username]

                # Update the existing user with the attributes of the new user
                existing_user.__dict__.update(user.__dict__)
                db[username] = existing_user
            else:
                # If the user does not exist, save it as usual
                db[username] = user

    @staticmethod
    def load_from_shelve(username):
        with shelve.open("user_db.shelve", writeback=True) as db:
            return db.get(username, None)

    @staticmethod
    def get_all_users():
        with shelve.open("user_db.shelve", writeback=True) as db:
            return list(db.values())

    @staticmethod
    def delete_user_from_shelve(username):
        with shelve.open("user_db.shelve", writeback=True) as db:
            if username in db:
                del db[username]

    @staticmethod
    def load_from_shelve_by_email(email):
        with shelve.open("user_db.shelve", writeback=True) as db:
            # Iterate through all users to find the one with the given email
            for user in db.values():
                if user.get_email() == email:
                    return user
        return None