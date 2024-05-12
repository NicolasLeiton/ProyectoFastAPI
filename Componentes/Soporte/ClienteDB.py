from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from Componentes.Soporte.Keys import *

db_client = MongoClient(MONGO_KEY, server_api=ServerApi('1'))

