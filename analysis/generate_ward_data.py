import json
import csv
import collections
execfile("utils.py")
execfile("LoLClasses.py")

summonerId = 68051502
inputFile = "../data/processed_match_data.json"
outputFile = "../data/wards.csv"
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
      if event['eventType'] != 'WARD_PLACED': continue
      document = flatten(event)
      document['matchId'] = game.matchId
      document = bool_to_bernoulli(document)

      # Save the kill location for use by deathheatmap.html
      heatmapevent = {}
      try:
        heatmapevent['x'] = event['position']['x']
        heatmapevent['y'] = event['position']['y']
        print event
      except:
        pass
      heatmapevent['time'] = event['timestamp']

      #if participantId = event['victimId'] and lane=="JUNGLE":
      heatmapevents.append(heatmapevent)

      if fieldnames is None:
        fieldnames = document.keys()
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
      writer.writerow(document)


with open("../data/wardlocations.js", "w") as f:
  f.write("data = ")
  json.dump(heatmapevents, f)
print len(heatmapevents), " wards places"