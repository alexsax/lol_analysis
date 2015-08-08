import json 
execfile('LolClasses.py')

settings_file = '../settings.json'
inputfilename = '../data/match_data.json'
outfilename = '../data/processed_match_data.json'

with open(settings_file) as f:    
  settings = json.load(f)

def create_participant_idx(game):
  participant_idx = {}
  for i, participant in enumerate(game['participantIdentities']):
    participant_idx[participant['participantId']] = i
  game['participantIdx'] = participant_idx
  return participant_idx

def add_frame_to_participant_timeline(participants, participant_id, frame, participant_idx):
  participants[participant_idx[int(participant_id)]]['frameTimeline'].append(frame)

def clean_5x5_summoners_rift(game):
  participants = game['participants']
  for i in xrange(len(game['teams'])):
    team = game['teams'][i]
    del team['dominionVictoryScore']
    del team['vilemawKills']
  for j in xrange(len(participants)):
    del participants[j]['stats']['totalPlayerScore']
    del participants[j]['stats']['objectivePlayerScore']
    del participants[j]['stats']['unrealKills']
    del participants[j]['stats']['totalScoreRank']
    del participants[j]['stats']['combatPlayerScore']

def split_timeline_into_participant_timelines(game, frames, participants, participant_idx):
  for i in xrange(len(participants)):
    participants[i]['frameTimeline'] = []

  game['eventTimeline'] = []
  for frame in frames:
    for participant_id, participantFrame in frame['participantFrames'].iteritems():
      del participantFrame['participantId']
      participantFrame['timestamp'] = frame['timestamp']
      add_frame_to_participant_timeline(participants, participant_id, participantFrame, participant_idx)
    if 'events' in frame:
      for event in frame['events']:
        game['eventTimeline'].append(event)

  del game['timeline']

def find_me(game):
  me = game['playerTeamAndChampion']
  participantId = None
  for participant in game['participants']:
    if participant['championId'] == me['championId'] and participant['teamId'] == me['teamId']:
      participantId = participant['participantId']
      break
  del game['playerTeamAndChampion']
  game['players'] = [{
    "summonerId": settings["summoner_id"],
    "summonerName": settings["summoner_name"],
    "participantId": participantId
  }]

def clean_game(game):
  frames = game['timeline']['frames'] # [1]['participantFrames']['1']  
  participants = game['participants']
  participant_idx = create_participant_idx(game)
  find_me(game)
  split_timeline_into_participant_timelines(game, frames, participants, participant_idx)
  if game['queueType'] in NORMAL_GAME_TYPES:
    clean_5x5_summoners_rift(game)
  else:
    print game['queueType']
  
if __name__ == "__main__":
  data = []
  for match in open(inputfilename):
    data.append(json.loads(match))
  for i in xrange(len(data)):
    clean_game(data[i])
  with open(outfilename, 'w') as outfile:
    json.dump(data, outfile)
