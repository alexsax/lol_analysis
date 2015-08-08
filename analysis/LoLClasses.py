NORMAL_GAME_TYPES = set(['NORMAL_5x5_BLIND', 'GROUP_FINDER_5x5', 'RANKED_SOLO_5x5', 'RANKED_DUO_5x5'])
TEAM_BUILDER_GAME_TYPE = set(['GROUP_FINDER_5x5'])
BOT_GAME_TYPES = set(['BOT_5x5_INTERMEDIATE'])


from collections import namedtuple
Position = namedtuple('Position', ['x','y'])
Rune = namedtuple('Rune', ['runeId','rank'])
Mastery = namedtuple('Mastery', ['masteryId','rank'])

class Stats:
  def __init__(self, **entries): 
    self.__dict__.update(entries)
  def __repr__(self):
    return str(self.__dict__)

class ParticipantFrame:
  def __init__(self, **entries): 
    self.__dict__.update(entries)
    if "position" in self.__dict__:
      self.position = Position(**self.position)
    else:
      self.position = None
  def __repr__(self):
    return str(self.__dict__)

class Participant:
  def __init__(self, **entries): 
    self.__dict__.update(entries)
    try:
      self.runes = [Rune(**rune) for rune in self.runes]
    except: pass
    try:
      self.masteries = [Mastery(**mastery) for mastery in self.masteries]
    except: pass
    self.frameTimeline = [ParticipantFrame(**frame) for frame in self.frameTimeline]
    self.stats = Stats(**self.stats)
  def __repr__(self):
    return str(self.__dict__)

class Player:
  def __init__(self, **entries): 
    self.__dict__.update(entries)
  def __repr__(self):
    return str(self.__dict__)


class Team:
  def __init__(self, **entries): 
    self.__dict__.update(entries)
  def __repr__(self):
    return str(self.__dict__)

class Game:
  def __init__(self, **entries): 
    self.__dict__.update(entries)
    self.participants = [Participant(**p) for p in self.participants]
    self.players = [Player(**p) for p in self.players]
    self.teams = [Team(**t) for t in self.teams]
  def summonerId(self, summonerName):
    for player in self.players:
      if player.summonerName == summonerName:
        return player.summonerId
    return None

  def participantId(self, summonerId):
    for player in self.players:
      if player.summonerId == summonerId:
        return player.participantId
    return None

  def participant(self, summonerId):
    return self.participants[self.participantIdx[str(self.participantId(summonerId))]]

  def teamId(self, summonerId):
    return self.participant(summonerId).teamId

  def team(self, summonerId):
    teamId = self.teamId(summonerId)
    for team in self.teams:
      if teamId == team.teamId:
        return team
    return None

  # Boolean if summoner's team won
  def teamByParticipantId(self, participantId):
    try:
      participant = self.participants[self.participantIdx[participantId]]
    except:
      participant = self.participants[self.participantIdx[str(participantId)]]
    teamId = participant.teamId
    for team in self.teams:
      if teamId == team.teamId:
        return team
    return None

  # Boolean if summoner's team won
  def winner(self, summonerId):
    return self.team(summonerId).winner


  # Boolean if summoner's team won
  def winnerByParticipantId(self, participantId):
    return self.teamByParticipantId(participantId).winner

  # Get participant stats returned by league API
  def stats(self, summonerId):
    return self.participant(summonerId).stats

  # Role summoner played
  def role(self, summonerId):
    return self.participant(summonerId).timeline['role']

  # Lane summoner played in
  def lane(self, summonerId):
    return self.participant(summonerId).timeline['lane']

  # Nth item bought by each participant (0-6)
  def item(self, summonerId, number):
    itemId = getattr(game.stats(summonerId), 'item' + str(number))
    participantId = game.participantId(summonerId)
    for event in self.eventTimeline:
      if event['eventType']=="ITEM_PURCHASED" and event['participantId']==participantId and itemId==event['itemId']:
        return event

  def firstDragon(self):
    for event in self.eventTimeline:
      if event['eventType'] == "ELITE_MONSTER_KILL" and event['monsterType']=="DRAGON":
        return event

  def firstBaron(self):
    for event in self.eventTimeline:
      if event['eventType'] == "ELITE_MONSTER_KILL" and event['monsterType']=="BARON_NASHOR":
        return event

  def is_standard_meta(self):
    participants = game.participants
    teams = {100:set(), 200:set()}
    required_roles = [('BOTTOM','DUO_SUPPORT'), ('BOTTOM', 'DUO_CARRY'), ('MIDDLE', 'SOLO'), ('TOP','SOLO'), ('JUNGLE', 'NONE')]
    for participant in participants:
      laneAndRole = (participant.timeline['lane'], participant.timeline['role'])
      teams[participant.teamId].add(laneAndRole)
    for teamid, lanesAndRoles in teams.items():
      for laneAndRole in required_roles:
        if laneAndRole not in lanesAndRoles:
          return False
    return True
    

  def __repr__(self):
    return str(self.__dict__)


