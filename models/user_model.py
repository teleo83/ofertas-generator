from flask_login import UserMixin
from bson.objectid import ObjectId
from extensions import mongo


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.email = user_data["email"]
        self.role = user_data.get("role", "user")
        self.active = user_data.get("active", True)
        self.plan = user_data.get("plan", "free")

    @staticmethod
    def get_by_id(user_id):
        try:
            user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            return None
        return None