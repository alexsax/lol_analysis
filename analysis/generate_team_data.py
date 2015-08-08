import json
import csv
import collections
execfile("utils.py")
execfile("LoLClasses.py")

summonerId = 68051502
inputFile = "../data/processed_match_data.json"
outputFile = "../data/teams.csv"
fieldnames = None

with open("champdict.json") as f:
  champs = json.load(f)

with open(outputFile, 'w') as outfile:
  with open(inputFile) as f:
    data = json.load(f)

  data = get_normal_games(data)
  documents = []
  fieldnames = set()
  for i, game in enumerate(data):
    game = Game(**game)
    # participantId = game.participantId(summonerId)
    # document = {}
    # team = game.team(summonerId)
    for team in game.teams:
      document = {}
      document = flatten(team.__dict__)
      document['matchId'] = game.matchId
      document = bool_to_bernoulli(document)
      documents.append(document)
      fieldnames.update(document.keys())

  writer = csv.DictWriter(outfile, fieldnames=fieldnames)
  writer.writeheader()
  for document in documents:
    writer.writerow(document)

