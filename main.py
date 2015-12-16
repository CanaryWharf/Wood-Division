# Main project

import json
import requests
import sys
import os
import bs4
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


def do_thing(name):
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
                                      'champ': champ_name,
                                      'spells': [spell1,
                                                 spell2],
                                      'team': item['teamId']}
    return skim


def lane(play_info):
    positions = {}
    remainder = ['Top', 'Mid', 'Bottom', 'Bottom', 'Jungle']
    champs = []
    for item in play_info:
        if item['spells'][0] == 'Smite' or item['spells'][1] == 'Smite':  # NOQA
            positions[item['champ']] = 'Jungle'
            remainder.remove('Jungle')
            continue
        champs.append(item['champ'])

    rejects = {}

    for cena in champs:
        soup = get_soup(
            'http://www.lolcounter.com/champions/%s', (cena))
        elems = soup.select('.block-tabs')
        possibles = elems[0].getText()
        possibles = possibles.strip('\n')
        possibles = possibles.split('\n')
        possibles.remove('All')
        possibles.remove('General')
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
        if count > 5:
            break
        for key in rejects:
            for item in rejects[key]:
                if item not in remainder:
                    rejects[key].remove(item)
            if len(rejects[key]) == 1:
                positions[key] = rejects[key][0]
                del rejects[key]
                remainder.remove(rejects[key][0])
    if rejects:
        for key in rejects:
            positions[key] = rejects[key]
    return positions


def strength(champ1, champ2):
    pass


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

skim = tester()

t1, t2 = teams(skim)

pprint(lane(t1))
