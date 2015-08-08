execfile("LoLClasses.py")

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def bool_to_bernoulli(document):
  for key, value in document.items():
    if value == True:
      document[key] = 1
    if value == False:
      document[key] = 0
  return document

def get_normal_games(data):
  return [game for game in data if game['queueType'] in NORMAL_GAME_TYPES]

def get_team_builder_games(data):
  return [game for game in data if game['queueType'] in TEAM_BUILDER_GAME_TYPE]

  