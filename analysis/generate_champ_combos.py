import json
import csv
import collections
from collections import defaultdict
from itertools import combinations
import operator
execfile("utils.py")
execfile("LoLClasses.py")

summonerId = 68051502
inputFile = "../data/processed_match_data.json"
outputFile = "../data/championcombos.csv"
fieldnames = None
chosen = 'leblanc'

with open("champdict.json") as f:
  champs = json.load(f)

with open(outputFile, 'w') as outfile:
  with open(inputFile) as f:
    data = json.load(f)

  data = get_normal_games(data)
  data.sort(key=lambda game: game["matchCreation"]) # Sort by time
  documents = []
  fieldnames = set()
  pairoutcomes = defaultdict(lambda: {'wins': 0, 'games': 0})
  singleoutcomes = defaultdict(lambda: {'wins': 0, 'games': 0})

  for i, game in enumerate(data):
    game = Game(**game)
    teams = {}
    winner = None
    for team in game.teams:
      teams[team.teamId] = []
      if team.winner: winner = team.teamId
    for participant in game.participants:

      teams[participant.teamId].append(champs[str(participant.championId)])

    for teamId, champions in teams.items():
      for pair in combinations(champions, 2):
        pair = tuple(sorted(pair))
        pairoutcomes[pair]['wins'] += 1 if teamId == winner else 0
        pairoutcomes[pair]['games'] += 1
      for champ in champions:
        singleoutcomes[champ]['wins'] += 1 if teamId == winner else 0
        singleoutcomes[champ]['games'] += 1


  best_champs = sorted(singleoutcomes.items(), key=lambda x: x[1]['wins']*1./x[1]['games'])

  def winrate(x):
    return x['wins']*1./x['games']

  def gain(champsDict):
    champ1 = champsDict[0][0]
    champ2 = champsDict[0][1]
    champ1WinRate = winrate(singleoutcomes[champ1])
    champ2WinRate = winrate(singleoutcomes[champ2])
    return winrate(champsDict[1])/max(champ1WinRate,champ2WinRate)

  def pad(x): return x + "\t" if len(x) < 8 else x
  best_champs = sorted(singleoutcomes.items(), key=lambda x: x[1]['wins']*1./x[1]['games'])

  best_pairs = sorted(pairoutcomes.items(), key=lambda x: gain(x))
  # for pair in best_pairs:
  #   if 'thresh' not in list(pair[0]): continue
  #   print pad(pair[0][0]), "\t", pad(pair[0][1]),  "\t", round(gain(pair), 2), "\t", pair[1]['games']

  for single in best_champs:
    if single[1]['games'] < 5: continue
    print pad(single[0]), "\t""\t", round(winrate(single[1]), 2), "\t", single[1]['games']






