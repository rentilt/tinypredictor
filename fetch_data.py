import os
import requests
import numpy as np
import time
from tqdm import trange
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get('API_KEY')

# get account info
game_id = "ZWYROO#EUW"
summoner_name, tag_line = game_id.split("#")
api_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag_line}"
api_url += '?api_key=%s' % API_KEY
res = requests.get(api_url)
my_info = res.json()
puuid = my_info['puuid']


# list all my matches
api_url = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+puuid+"/ids?start=0&count=100"
api_url += '&api_key=%s' % API_KEY
res = requests.get(api_url)
matches = res.json()



# fetch dataset: if file not found, create empty lists
try: 
    dataset = np.load('./data/dataset.npy').tolist()
    targets = np.load('./data/targets.npy').tolist()
    matches_id = np.load('./data/matches_id.npy').tolist()
except OSError:
    cont = eval(input("Failed to load dataset...\nCreate new dataset from scratch? (Y/N)"))
    if cont == 'Y':
        dataset = []
        targets = []
        matches_id = []
    else: exit(0)

number_of_games = len(dataset)

for match_id in matches:
    
    # fetch match information: 
    #   - sleep for a minute if rate limit exceeded
    while(True):
        try:
            api_url = "https://europe.api.riotgames.com/lol/match/v5/matches/"+match_id
            api_url += '?api_key=%s' % API_KEY
            res = requests.get(api_url)
            match = res.json()
            info = match['info']
            break
        except Exception:
            print("Rate limit exceeded: sleeping for 60s...")
            for zzz in (t := trange(60)):
                time.sleep(1)

    # skip aram games
    if 'ARAM' in info['gameMode']:
        continue
    
    # skip duplicated games
    if match_id in matches_id:
        continue

    matches_id.append(match_id)
    number_of_games += 1

    # game duration:    Treat the value as milliseconds if the gameEndTimestamp 
    #                   field isn't in the response and to treat the value as seconds 
    #                   if gameEndTimestamp is in the response.
    try:
        _ = info['gameEndTimestamp']
        duration = info['gameDuration'] 
    except Exception:
        duration = info['gameDuration'] * 1000
    game_duration = np.array([[duration] * 4])


    teams = info['teams']
    players = info['participants']

    team_ids = [x['teamId'] for x in teams]
    data = []

    # players scores and info
    for id in team_ids:
        for x in players:
            if x['teamId'] == id:
                try:
                    kd = x['kills'] / x['deaths']
                except ZeroDivisionError:
                    kd = x['kills']
                data.append((x['championId'], x['champLevel'], kd, x['goldEarned']))
    data = np.array(data)


    # team objectives
    # kills | towers | inhibitors | dragons | barons 
    team_0 = teams[0]['objectives']
    team_0_objectives = np.array([[ team_0['champion']['kills'], team_0['tower']['kills'], team_0['inhibitor']['kills'],
                         team_0['dragon']['kills'], team_0['baron']['kills'] ] ]*4).T
    team_1 = teams[1]['objectives']
    team_1_objectives = np.array([ [team_1['champion']['kills'], team_1['tower']['kills'], team_1['inhibitor']['kills'],
                         team_1['dragon']['kills'], team_1['baron']['kills'] ]]*4).T

    # game state dataset
    data = np.concatenate((data[0:5,:],team_0_objectives, data[5:,:], team_1_objectives, game_duration))

    # target
    win = 0 if teams[0]['win'] == True else 1
    dataset.append(data)
    targets.append(win)
    if number_of_games % 5 == 0:
        print(f'saving {number_of_games} games')
        np.save('./data/dataset.npy', np.array(dataset))
        np.save('./data/targets.npy', np.array(targets))
        np.save('./data/matches_id.npy', np.array(matches_id))
