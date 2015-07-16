settings_file = 'settings.json'
max_download_attempts = 10
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import datetime

# Instantiate connection to DB
client = MongoClient()
db = client.lol_database
collection = db.match_data

from riotwatcher import RiotWatcher
from riotwatcher import error_429, error_500, error_503
import json
import time
import logging

def match_download_failed(match_id, attempt, error, logger):
  if attempt < max_download_attempts-1:
    logger.warning("Failed to download match " + str(match_id) + " because of " + str(error) + ": retrying.")
  else:
    logger.error("Failed to download match " + str(match_id) + "! Moving on.")

def download_matches(w, max_matches, logger):
  # First we need to retreive the match ID's, and then we get the matches one by one
  recent_games = w.get_recent_games(summoner_id)["games"]
  game_ids = [game["gameId"] for game in recent_games][:max_matches] # only want the last 9 since we're call-restricted
  histories = []
  for game_id in game_ids:
    for attempt in range(max_download_attempts):
      try:
        next_game = w.get_match(game_id, include_timeline=True)
      except (error_429, error_500, error_503) as e:      
        match_download_failed(game_id, attempt, error, logger)
        time.sleep(1)
      histories.append(next_game)
      break
  return histories

def insert_matches(collection, recent_game_histories):
  try:
    collection.insert_many(recent_game_histories, ordered=False)
  except BulkWriteError:
    pass

if __name__ == "__main__":
  with open(settings_file) as f:    
    settings = json.load(f)

  logger = logging.getLogger('lol_aggregator')
  logger.setLevel(logging.WARNING)
  
  w = RiotWatcher(settings['api_key'])
  summoner_id = settings['summoner_id']
  calls_per_10 = settings['max_calls_per_10s']

  recent_game_histories = download_matches(w, max_matches=calls_per_10-1, logger=logger)
  insert_matches(collection, recent_game_histories)


client.close()
