from pymongo import MongoClient
import json
settings_file = 'settings.json'
with open(settings_file) as f:    
  settings = json.load(f)

# Instantiate connection to DB
client = MongoClient(settings["db_uri"])
db = client[settings["db_name"]]
collection = db.match_data

collection.create_index('matchId', unique=True)

client.close()