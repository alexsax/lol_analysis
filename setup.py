from pymongo import MongoClient

# Instantiate connection to DB
client = MongoClient()
db = client.lol
collection = db.match_data

collection.create_index('matchId', unique=True)

client.close()