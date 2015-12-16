# Main project

import json
import requests
import sys
import os
import bs4
import re
from pprint import pprint
config_file = 'config.json'
if not os.path.isfile(config_file):
    sys.exit('No config File')
filename = open(config_file, 'r')
config = json.load(filename)
filename.close()
summoner = config['summoner']
api_key = config['api_key']
url = config['url']
global_url = config['global']
server = config['server']
region = config['region']


def tester():
    filename = open('testdata.json', 'r')
    skim = json.load(filename)
    filename.close()
    return skim


def get_data(stuff, argtings):
    response = requests.get(stuff % argtings)
    response.raise_for_status()
    return json.loads(response.text)


def get_soup(stuff, argtings):
    res = requests.get(stuff % argtings)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    return soup


def match_data(name):
    dic = get_data(
        '%s/api/lol/euw/v1.4/summoner/by-name/%s?api_key=%s', (url,
                                                               name,
                                                               api_key))
    id = dic[name.lower()]['id']
    dic = get_data(
        '%s/observer-mode/rest/consumer/getSpectatorGameInfo/%s/%s?api_key=%s',
        (url, server, id, api_key))
    fat = dic['participants']
    skim = {}
    for item in fat:
        dic = get_data(
            '%s/api/lol/static-data/%s/v1.2/champion/%s?api_key=%s',  # NOQA
            (global_url, region, item['championId'], api_key))
        champ_name = dic['key']
        dic = get_data(
            '%s//api/lol/static-data/%s/v1.2/summoner-spell/%s?api_key=%s',
            (global_url, region, item['spell1Id'], api_key))
        spell1 = dic['name']
        dic = get_data(
            '%s//api/lol/static-data/%s/v1.2/summoner-spell/%s?api_key=%s',
            (global_url, region, item['spell2Id'], api_key))
        spell2 = dic['name']
        skim[item['summonerName']] = {'id': item['summonerId'],
                                      'champ_id': item['championId'],
                                      'champ': champ_name,
                                      'spells': [spell1,
                                                 spell2],
                                      'team': item['teamId']}
    return skim


def lane(play_info):
    posfile = open('champ_pos.json', 'r')
    pos = json.load(posfile)
    posfile.close()
    positions = {}
    remainder = ['Top', 'Mid', 'Bottom', 'Bottom', 'Jungler']
    champs = []
    for item in play_info:
        if item['spells'][0] == 'Smite' or item['spells'][1] == 'Smite':  # NOQA
            positions[item['champ']] = 'Jungler'
            remainder.remove('Jungler')
            continue
        champs.append(item['champ'])

    rejects = {}

    for cena in champs:
        possibles = pos[cena]
        if 'Jungler' not in remainder:
            if 'Jungler' in possibles:
                possibles.remove('Jungler')
        if len(possibles) == 1:
            positions[cena] = possibles[0]
            remainder.remove(possibles[0])
            continue
        rejects[cena] = possibles
    count = 0
    while remainder:
        count += 1
        if count > 30:
            break
        # What is left
        for key in rejects:
            for item in rejects[key]:
                if item not in remainder:
                    rejects[key].remove(item)
            if len(rejects[key]) == 1:
                positions[key] = rejects[key][0]
                remainder.remove(rejects[key][0])
        # Only they can x lane
        current_count = {}
        for key in rejects:
            for item in current_count:
                if item in current_count.keys():
                    current_count[item] += 1
                else:
                    current_count
        for key in current_count:
            if current_count[key] == 1:
                for item in rejects:
                    if key in item:
                        positions[key] = item
                        remainder.remove(item)
    if remainder:
        for key in rejects:
            positions[key] = rejects[key]
    return positions


def teams(fams):
    friend = []
    bully = []
    own_team = fams[summoner]['team']
    for key in fams:
        if fams[key]['team'] == own_team:
            friend.append(fams[key])
        else:
            bully.append(fams[key])
    return friend, bully


def player_info(sid, cid):
    c = {}
    data = get_data(
        '%s/api/lol/%s/v1.3/stats/by-summoner/%s/ranked?api_key=%s',
        (url, region, sid, api_key))
    c = data['champions']
    stats = {}
    for item in c:
        if item['id'] == cid:
            stats = item['stats']
            break
    if not stats:
        return ['Cherry Popped']
    else:
        return ['%.2f' % (stats['totalChampionKills']/stats['totalDeathsPerSession']),  # NOQA
            '%.2f' % (stats['totalAssists']/stats['totalSessionsPlayed']),
            '%.2f' % (stats['totalSessionsWon']/stats['totalSessionsLost']),
            str(stats['totalSessionsPlayed'])]


def counter_rating(friend, bully):
    soup = get_soup('http://www.lolcounter.com/champions/%s/weak',
                    (bully))
    weak = soup.select('.weak-block .name')
    for item in weak:
        if item.getText() == friend:
            return 'green'
    soup = get_soup('http://www.lolcounter.com/champions/%s/strong',
                    (bully))
    strong = soup.select('.weak-block .name')
    for item in strong:
        if item.getText() == friend:
            return 'red'
    return 'yellow'


def counter_tips(friend, bully):
    soup = get_soup(
        'http://www.lolcounter.com/champions/%s/%s',
        (bully, friend))
    data = soup.select('.tip-block ._tip')
    gentips = []
    for item in data:
        gentips.append(item.getText())
    soup = get_soup(
        'http://www.lolcounter.com/tips/%s/%s',
        (bully, friend))
    data = soup.select('._tip')
    spectips = []
    for item in data:
        spectips.append(item.getText())
    return [gentips, spectips]


def matchup(friendlies, bullies):
    pass


def run():
    skim = tester()
    friendlies, bullies = teams(skim)
    friendlylane = lane(friendlies)
    bullylane = lane(bullies)
    print(friendlylane)


if __name__ == "__main__":
    run()
