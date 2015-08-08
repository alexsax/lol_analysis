import json
import csv
import collections
from collections import defaultdict
execfile("utils.py")
execfile("LoLClasses.py")

summonerId = 68051502
inputFile = "../data/processed_match_data.json"
outputFile = "../data/lanes.csv"


with open("champdict.json") as f:
  champs = json.load(f)


def get_gold_diff_per_min_delta(participant, participantMatches):
  resource = 'goldPerMinDeltas'
  diffs = {}
  participantMatch = participantMatches[participant.participantId]
  for time, amount in participant.timeline[resource].items():
    diffs['goldDiffPerMin_'+time] = amount- participantMatch.timeline[resource][time]
  return diffs

def kills_deaths_assists_before_ten(game):
  killsAndAssists = defaultdict(lambda: {'kills': 0, 'deaths':0,'assists':0})
  for event in game.eventTimeline:
    if event['eventType'] != 'CHAMPION_KILL': continue
    if event['timestamp'] > 10*60*1000: continue   # After 10 mins
    if event['killerId'] == 0: continue # Ignore executions
    killsAndAssists[event['killerId']]['kills'] += 1
    killsAndAssists[event['victimId']]['deaths'] += 1
    if 'assistingParticipantIds' in event:
      for assistingParticipantId in event['assistingParticipantIds']:
        killsAndAssists[assistingParticipantId]['assists'] += 1
  return killsAndAssists

with open(outputFile, 'w') as outfile:
  with open(inputFile) as f:
    data = json.load(f)
  fieldnames = set()
  documents = []
  data = get_normal_games(data)

  for game in data:
    game = Game(**game)
    if not game.is_standard_meta(): continue
    participantMatches = {}

    # Match up lane opponents
    for participant in game.participants:
      laneAndRole = participant.timeline['lane'] + participant.timeline['role']
      if laneAndRole in participantMatches:
        participantMatches[participant.participantId] = participantMatches[laneAndRole]
        participantMatches[participantMatches[laneAndRole].participantId] = participant
        del participantMatches[laneAndRole]
      else:
        participantMatches[laneAndRole] = participant

    # get kills and assists for each participant
    KDAtten = kills_deaths_assists_before_ten(game)

    # Create documents for game
    for participant in game.participants:
      document = flatten(participant.timeline)
      gold_diffs = get_gold_diff_per_min_delta(participant, participantMatches)
      document.update(gold_diffs)
      document['killsAtTen'] = KDAtten[participant.participantId]['kills']
      document['deathsAtTen'] = KDAtten[participant.participantId]['deaths']
      document['assistsAtTen'] = KDAtten[participant.participantId]['assists']
      document['matchid'] = game.matchId
      document['teamid'] = participant.teamId
      document['winner'] = participant.stats.winner
      document = bool_to_bernoulli(document)
      fieldnames = fieldnames.union(document.keys())
      documents.append(document)

  writer = csv.DictWriter(outfile, fieldnames=fieldnames)
  writer.writeheader()
  for document in documents:
    writer.writerow(document)
