settings_file = 'settings.json'
max_download_attempts = 10


from pymongo import MongoClient
from pymongo.errors import BulkWriteError, DuplicateKeyError
from riotwatcher import RiotWatcher
from riotwatcher import error_429, error_500, error_503, error_404
import time
import logging
import json
import datetime

with open(settings_file) as f:    
  settings = json.load(f)

# Instantiate connection to DB
client = MongoClient(settings["db_uri"])
db = client[settings["db_name"]]
collection = db.match_data


def match_download_failed(match_id, attempt, error, logger):
  if attempt < max_download_attempts-1:
    logger.warning("Failed to download match " + str(match_id) + " because of " + str(error) + ": retrying.")
  else:
    logger.error("Failed to download match " + str(match_id) + "! Moving on.")

def download_matches(w, max_matches, logger):
  # First we need to retreive the match ID's, and then we get the matches one by one
  recent_games = w.get_recent_games(summoner_id)["games"]
  game_ids = [game["gameId"] for game in recent_games][:max_matches] # only want the last 9 since we're call-restricted
  game_to_participant = {}
  for game in recent_games:
    game_to_participant[game["gameId"]] = {
        "championId": game["championId"],
        "teamId": game["teamId"]
    }
  histories = []
  for game_id in game_ids:
    for attempt in range(max_download_attempts):
      try:
        print game_id
        next_game = w.get_match(game_id, include_timeline=True)
      except Exception as error:      
        match_download_failed(game_id, attempt, error, logger)
        time.sleep(1)

      next_game['playerTeamAndChampion'] = game_to_participant[game_id]
      histories.append(next_game)
      break
  return histories

def insert_matches(collection, recent_game_histories):
  try:
    collection.insert(recent_game_histories, continue_on_error=True)
  except (BulkWriteError, DuplicateKeyError) as e:
    pass

if __name__ == "__main__":
  logger = logging.getLogger('lol_aggregator')
  logger.setLevel(logging.WARNING)
  
  w = RiotWatcher(settings['api_key'])
  summoner_id = settings['summoner_id']
  calls_per_10 = settings['max_calls_per_10s']

  recent_game_histories = download_matches(w, max_matches=calls_per_10-1, logger=logger)
  insert_matches(collection, recent_game_histories)

client.close()
