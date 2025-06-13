from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_pymongo import PyMongo

bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()
mongo = PyMongo()
