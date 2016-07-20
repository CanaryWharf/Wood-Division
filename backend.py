import simplejson as json
import requests
from pprint import pprint

filename = open('config.json')
config = json.load(filename)
filename.close()


def get_data(url, argtings):
    response = requests.get(url % argtings)
    response.raise_for_status()
    try:
        return json.loads(response.text)
    except json.scanner.JSONDecodeError:
        return None


def get_match(test=True):
    if not test:
        data = get_data('%s/observer-mode/rest/consumer/getSpectatorGameInfo/%s/%s?api_key=%s',  # NOQA
                        (config['url'],
                         config['platform'],
                         config['id'],
                         config['api_key']))
    else:
        filename = open('raw_testdata.json')
        data = json.load(filename)
        filename.close()
    friendly = None
    for item in data['participants']:
        print(item['summonerId'])
        if item['summonerId'] == config['id']:
            friendly = item['teamId']
            break
    friendlies, bullies = [], []
    for item in data['participants']:
        if item['teamId'] == friendly:
            friendlies.append(item)
        else:
            bullies.append(item)

    return friendlies, bullies


def get_league(summoners):
    data = get_data('%s/api/lol/%s/v2.5/league/by-summoner/%s/entry?api_key=%s',  # NOQA
                    (config['url'],
                     config['region'],
                     ','.join(summoners),
                     config['api_key']))
    output = {}
    for key in data.keys():
        for item in data[key]:
            if item['queue'] == 'RANKED_SOLO_5x5':
                output[key] = item
                break
    return output


def get_mastery(summoner, champ):
    data = get_data('%s/championmastery/location/%s/player/%d/champion/%d?api_key=%s',  # NOQA
                    (config['url'],
                     config['platform'],
                     summoner,
                     champ,
                     config['api_key']))
    return data


def get_champ(champ_id):
    data = get_data('%s/api/lol/static-data/%s/v1.2/champion/%d?api_key=%s',
                    (config['global'],
                     config['region'],
                     champ_id,
                     config['api_key']))
    return data

pprint(get_champ(103))
