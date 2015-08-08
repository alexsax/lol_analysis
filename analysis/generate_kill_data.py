import json
import csv
import collections
execfile("utils.py")
execfile("LoLClasses.py")

summonerId = 68051502
inputFile = "../data/processed_match_data.json"
outputFile = "../data/kills.csv"
fieldnames = None

with open("champdict.json") as f:
  champs = json.load(f)

with open(outputFile, 'w') as outfile:
  with open(inputFile) as f:
    data = json.load(f)
  eventTypes = set()
  data = get_normal_games(data)
  heatmapevents = []
  for game in data:
    game = Game(**game)
    lane = game.participant(summonerId).timeline['lane']
    participantId = game.participantId(summonerId)

    for event in game.eventTimeline:
      eventTypes.add(event['eventType'])
      if event['eventType'] != 'CHAMPION_KILL': continue

      # List number of assists
      if 'assistingParticipantIds' in event:
        event['n_assists'] = len(event['assistingParticipantIds'])
        if participantId in event['assistingParticipantIds']:
          event['assist'] = True
        else: 
          event['assist'] = False
        del event['assistingParticipantIds']
      else :
        event['assist'] = False
        event['n_assists'] = 0

      document = flatten(event)
      document['matchId'] = game.matchId
      if event['killerId'] != 0 and event['killerId'] != '0':  # Don't want executions
        document['killerTeam'] = game.teamByParticipantId(event['killerId']).teamId
        document['killerTeamWinner'] = game.teamByParticipantId(event['killerId']).winner
      document = bool_to_bernoulli(document)

      # Save the kill location for use by deathheatmap.html
      heatmapevent = {}
      heatmapevent['x'] = event['position']['x']
      heatmapevent['y'] = event['position']['y']
      heatmapevent['time'] = event['timestamp']

      #if participantId = event['victimId'] and lane=="JUNGLE":
      heatmapevents.append(heatmapevent)

      if fieldnames is None:
        fieldnames = document.keys()
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
      writer.writerow(document)


with open("../data/killocations.js", "w") as f:
  f.write("data = ")
  json.dump(heatmapevents, f)
print "Wrote ", len(heatmapevents), " deaths"