import json
import csv
import collections
execfile("utils.py")
execfile("LoLClasses.py")

summonerId = 68051502
fieldnames = set()

with open('../data/basic_stats.csv', 'w') as outfile:
  with open('../data/processed_match_data.json') as f:
    data = json.load(f)
  documents = []
  data = get_normal_games(data)
  for game in data:
    game = Game(**game)

    document = {}
    document.update(game.team(summonerId).__dict__)
    document['matchDuration'] = game.matchDuration
    document['queueType'] = game.queueType
    document['matchCreation'] = game.matchCreation
    document.update(game.stats(summonerId).__dict__)
    document.update(flatten(game.participant(summonerId).timeline))
    document = bool_to_bernoulli(document)
    documents.append(document)
    fieldnames.update(document.keys())

  writer = csv.DictWriter(outfile, fieldnames=fieldnames)
  writer.writeheader()
  for document in documents:
    writer.writerow(document)
