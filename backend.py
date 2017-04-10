import simplejson as json
import requests

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

def load_match(config):
    pass


def get_version(config):
    data = get_data('%s/api/lol/static-data/%s/v1.2/versions?api_key=%s',
                    (config['global'],
                     config['region'],
                     config['api_key']))  # NOQa
    return data[0]


def get_config(new_name, region, apikey):
    sumdata = get_data('%s/api/lol/%s/v1.4/summoner/by-name/%s?api_key=%s',
                       ('https://%s.api.pvp.net' % region.lower(),
                        region.lower(),
                        new_name,
                        apikey))
    if not sumdata:
        return False
    con = {}
    con['api_key'] = apikey
    con['summoner'] = new_name
    con['region'] = region.lower()
    con['platform'] = endpoints[region]
    con['url'] = 'https://%s.api.pvp.net' % region.lower()
    con['id'] = sumdata[
        ''.join(c.lower() for c in new_name if not c.isspace())]['id']
    con['version'] = get_version()
    return con


def get_data(url, argtings):
    """Retrieves data from url using selected arguments"""
    response = requests.get(url % argtings)
    print(response.text)
    if response.status_code == 404 or response.status_code == 403:
        return None
    try:
        return json.loads(response.text)
    except json.scanner.JSONDecodeError:
        return None


def get_match(config, test=False):
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


def get_league(summoners, config):
    """retrieves Division information for players. Accepts up to 10 players"""
    data = get_data('%s/api/lol/%s/v2.5/league/by-summoner/%s/entry?api_key=%s',  # NOQA
                    (config['url'],
                     config['region'],
                     ','.join(map(str, summoners)),
                     config['api_key']))
    output = {}
    for key in data.keys():
        for item in data[key]:
            if item['queue'] == 'RANKED_SOLO_5x5':
                output[key] = item
                break
    return output


def get_champ_mastery(summoner, champ, config):
    """retrieves champion mastery informatiion"""
    data = get_data('%s/championmastery/location/%s/player/%d/champion/%d?api_key=%s',  # NOQA
                    (config['url'],
                     config['platform'],
                     int(summoner),
                     int(champ),
                     config['api_key']))
    return data


def get_champ(champ_id, config):
    """retrieves static champion data"""
    data = get_data('%s/api/lol/static-data/%s/v1.2/champion/%d?champData=passive,image,spells&api_key=%s',  # NOQA
                    (config['global'],
                     config['region'],
                     champ_id,
                     config['api_key']))
    return data


def get_masteries(config):
    """retrieve static mastery data"""
    data = get_data('%s/api/lol/static-data/%s/v1.2/mastery?masteryListData=image&api_key=%s',  # NOQA
                    (config['global'],
                     config['region'],
                     config['api_key']))
    return data


def get_runes(config):
    """retrieve static rune data"""
    data = get_data('%s/api/lol/static-data/%s/v1.2/rune?runeListData=image&api_key=%s',  # NOQA
                    (config['global'],
                     config['region'],
                     config['api_key']))
    return data


def get_spells(sid, config):
    """retrieve static spell data"""
    data = get_data('%s/api/lol/static-data/%s/v1.2/summoner-spell/%d?api_key=%s',  # NOQA
                    (config['global'],
                     config['region'],
                     sid,
                     config['api_key']))
    return data
