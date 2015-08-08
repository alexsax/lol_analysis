import json
import csv
import collections
execfile("utils.py")
execfile("LoLClasses.py")

summonerId = 68051502
inputFile = "../data/processed_match_data.json"
outputFile = "../data/locations.csv"
fieldnames = None

with open("champdict.json") as f:
  champs = json.load(f)

with open(outputFile, 'w') as outfile:
  with open(inputFile) as f:
    data = json.load(f)

  data = get_normal_games(data)
  fields = set()
  heatmapevents = []
  for game in data:
    game = Game(**game)
    jgParticipantIds = [participant.participantId for participant in game.participants if participant.timeline['lane'] == "JUNGLE"]
    winners = set([participant.participantId for participant in game.participants if participant.stats.winner == True])
    participantId = game.participantId(summonerId)

    for participant in game.participants:
      lane = participant.timeline['lane']
      for participantFrame in participant.frameTimeline:
        document = flatten(participantFrame.__dict__)
        document['matchId'] = game.matchId
        document = bool_to_bernoulli(document)
        if fieldnames is None:
          fieldnames = document.keys()
          writer = csv.DictWriter(outfile, fieldnames=fieldnames)
          writer.writeheader()
        writer.writerow(document)
        if participantFrame.position is None: continue
        heatmapevent = {}
        heatmapevent['x'] = participantFrame.position.x
        heatmapevent['y'] = participantFrame.position.y
        heatmapevent['time'] = participantFrame.timestamp
        #heatmapevent['lane'] = lane
        if lane == "JUNGLE" and participant.participantId in jgParticipantIds and participantId in winners:
          heatmapevents.append(heatmapevent)


with open("../data/locations.js", "w") as f:
  f.write("data = ")
  json.dump(heatmapevents, f)
print "Wrote ", len(heatmapevents), " location"