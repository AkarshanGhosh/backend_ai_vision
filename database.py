from server.extensions import mongo

class Database:
    @staticmethod
    def get_users_collection():
        return mongo.db.users

    @staticmethod
    def get_blogs_collection():
        return mongo.db.blogs
