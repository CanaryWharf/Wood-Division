import simplejson as json
import requests

filename = open('config.json')
config = json.load(filename)
filename.close()
endpoints = {
    'BR': 'BR1',
    'EUNE': 'EUN1',
    'EUW': 'EUW1',
    'JP': 'JP1',
    'KR': 'KR',
    'LAN': 'LA1',
    'LAS': 'LA2',
    'NA': 'NA1',
    'OCE': 'OC1',
    'TR': 'TR1',
    'RU': 'RU',
    'PBE': 'PBE1'
}


def change_name(new_name, region):
    sumdata = get_data('%s/api/lol/%s/v1.4/summoner/by-name/%s',
                       (config['global'],
                        region.lower(),
                        new_name))
    if not sumdata:
        return False
    filename = open('config.json', 'r+')
    con = json.load(filename)
    con['summoner'] = new_name
    con['region'] = region.lower()
    con['platform'] = endpoints['region']
    con['url'] = 'https://%s.api.pvp.net' % region.lower()
    con['id'] = sumdata[
        ''.join(c.lower() for c in new_name if not c.isspace())]['id']
    json.dump(con, filename)
    filename.locse()
    return True


def get_data(url, argtings):
    """Retrieves data from url using selected arguments"""
    response = requests.get(url % argtings)
    if response.status_code == 404:
        return None
    try:
        return json.loads(response.text)
    except json.scanner.JSONDecodeError:
        return None


def get_match(test=True):
    """Retrieves current match data. If test, it will use testdata"""
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
    if data is None:
        return None
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
    """retrieves Division information for players. Accepts up to 10 players"""
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


def get_champ_mastery(summoner, champ):
    """retrieves champion mastery informatiion"""
    data = get_data('%s/championmastery/location/%s/player/%d/champion/%d?api_key=%s',  # NOQA
                    (config['url'],
                     config['platform'],
                     summoner,
                     champ,
                     config['api_key']))
    return data


def get_champ(champ_id):
    """retrieves static champion data"""
    data = get_data('%s/api/lol/static-data/%s/v1.2/champion/%d?api_key=%s',
                    (config['global'],
                     config['region'],
                     champ_id,
                     config['api_key']))
    return data


def get_masteries(mid):
    """retrieve static mastery data"""
    data = get_data('%s/api/lol/static-data/%s/v1.2/mastery/%d?api_key=%s',
                    (config['global'],
                     config['region'],
                     mid,
                     config['api_key']))
    return data


def get_runes(rid):
    """retrieve static rune data"""
    data = get_data('%s/api/lol/static-data/%s/v1.2/rune/%d?api_key=%s',
                    (config['global'],
                     config['region'],
                     rid,
                     config['api_key']))
    return data


def get_spells(sid):
    """retrieve static spell data"""
    data = get_data('%s/api/lol/static-data/%s/v1.2/summoner-spell/%d?api_key=%s',  # NOQA
                    (config['global'],
                     config['region'],
                     sid,
                     config['api_key']))
    return data
