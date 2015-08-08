import json
import csv
import collections
execfile("utils.py")
execfile("LoLClasses.py")

summonerId = 68051502
inputFile = "../data/processed_match_data.json"
outputFile = "../data/matches.csv"
fieldnames = None

with open("champdict.json") as f:
  champs = json.load(f)

def get_streak(documents, current_doc, i):
  if i == 0: return 1
  else: # If the streak just began or if this game took place much later (2 hrs) than the last
    if documents[i-1]['winner'] != current_doc['winner'] or current_doc['matchCreation'] - documents[i-1]['matchCreation'] > 2*60*60*1000:
      return 1
    else:
      return documents[i-1]['streak'] + 1

def fast_requeue(documents, current_doc, i):
  if i == 0: return True
  else: 
    return (current_doc['matchCreation'] - documents[i-1]['matchCreation'] <= 2*60*60*1000)


with open(outputFile, 'w') as outfile:
  with open(inputFile) as f:
    data = json.load(f)

  data = get_normal_games(data)
  data.sort(key=lambda game: game["matchCreation"]) # Sort by time
  documents = []
  fieldnames = set()
  for i, game in enumerate(data):
    game = Game(**game)

    participantId = game.participantId(summonerId)
    firstBaron = game.firstBaron()
    firstDragon = game.firstDragon()
    document = {}
    # Participant info
    document['participantId'] = game.participantId(summonerId)
    document['participantChampionId'] = game.participant(summonerId).championId
    document['participantChampion'] = champs[str(document['participantChampionId'])]
    document['role'] = game.role(summonerId)
    document['lane'] = game.lane(summonerId)
    document['winner'] = game.winner(summonerId)

    document['firstBaronTime'] = firstBaron['timestamp'] if firstBaron else None
    document['firstDragonTime'] = firstDragon['timestamp'] if firstDragon else None
    items = [game.item(summonerId, j) for j in range(4)]
    for j, item in enumerate(items):
      document['timeToItem'+str(j)] = item['timestamp'] if item is not None else None

    # Match info
    document['queueType'] = game.queueType
    document['matchDuration'] = game.matchDuration
    document['matchCreation'] = game.matchCreation
    document['matchId'] = game.matchId
    document['streak'] = get_streak(documents, document, i)
    document['wonLastGame'] = documents[i-1]['winner'] if i > 0 else True
    document['fastRequeue'] = fast_requeue(documents, document, i)
    document['winner'] = game.winner(summonerId)
    document = bool_to_bernoulli(document)
    documents.append(document)
    fieldnames.update(document.keys())

  writer = csv.DictWriter(outfile, fieldnames=fieldnames)
  writer.writeheader()
  for document in documents:
    writer.writerow(document)

