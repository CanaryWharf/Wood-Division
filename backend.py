import simplejson as json
from pprint import pprint
import requests
import time
import re


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


def get_stats(playalist, config, results):
    for item in playalist:
        if str(item['summonerId']) in results.keys():
            item['league'] = results[str(item['summonerId'])]['tier'] + ' ' + results[str(item['summonerId'])]['entries'][0]['division']  # NOQA
        else:
            item['league'] = 'TRUE WOOD'
        item['champMastery'] = get_champ_mastery(item['summonerId'],
                                                 item['championId'],
                                                 config)
    return playalist


def parse_runes(desc, count):
    regex = r'([+-]\d+\.?\d*\%?) ([\(\)\s\w]+)'
    s = re.findall(regex, desc)
    output = ""
    for item in s:
        percent = False
        if item[0].endswith("%"):
            percent = True
            num = item[0].strip('%')
        else:
            num = item[0]
        x = float(num) * count
        if x >= 0:
            output += "+"
        output += str(x)
        if percent:
            output += "%"
        output += " "
        output += item[1]
    return output



def sanitisedat(playas, runedata, masterydata, spelldata, champdata, config, friend):  # NOQA
    ddragon = 'http://ddragon.leagueoflegends.com/cdn/%s/img' % config['version']  # NOQA
    output = []
    for item in playas:
        entry = {}
        entry['champMastery'] = item['champMastery']['championLevel']
        entry['league'] = item['league']
        entry['summoner'] = item['summonerName']
        entry['nameid'] = str(item['summonerId'])
        entry['masteries'] = []
        for m in item['masteries']:
            n = {}
            dat = masterydata['data'][str(m['masteryId'])]
            n['name'] = dat['name']
            n['desc'] = dat['description'][m['rank']-1]
            n['image'] = '%s/mastery/%s' % (ddragon, dat['image']['full'])
            entry['masteries'].append(n)
        entry['runes'] = []
        for r in item['runes']:
            count = r['count']
            x = {}
            dat = runedata['data'][str(r['runeId'])]
            x['image'] = '%s/rune/%s' % (ddragon, dat['image']['full'])
            x['desc'] = parse_runes(dat['sanitizedDescription'], count)
            entry['runes'].append(x)
        entry['Dkey'] = spelldata[str(item['spell1Id'])]
        entry['Dkey']['image'] = '%s/spell/%s' % (ddragon, entry['Dkey']['filename'])
        print(entry['Dkey'])
        entry['Fkey'] = spelldata[str(item['spell2Id'])]
        entry['Fkey']['image'] = '%s/spell/%s' % (ddragon, entry['Fkey']['filename'])
        # Champion Data
        c = champdata[str(item['championId'])]
        entry['champ'] = c['name']
        entry['key'] = c['key']
        entry['image'] = "%s/champion/%s" % (ddragon, c['image'])
        if friend:
            entry['tips'] = c['allytips']
        else:
            entry['tips'] = c['enemytips']
        entry['passive'] = {
            'image': "%s/passive/%s" % (ddragon, c['passive']['image']['full']),
            'desc' : c['passive']['sanitizedDescription']
        }

        entry['spells'] = []
        # Still misssing shit on ritos end
        for spell in c['spells']:
            x = {
                'image' : "%s/spell/%s" % (ddragon, spell['image']['full']),
                'cooldown' :spell['cooldownBurn'],
                'desc' : spell['sanitizedDescription']

            }
            entry['spells'].append(x)

        output.append(entry)

    return output



def fix_your_champs_rito(champdata):
    output = {}
    for item in champdata['data'].values():
        entry = {
            'name': item['name'],
            'image': item['image']['full'],
            'title': item['title'],
            'enemytips': item['enemytips'],
            'allytips': item['allytips'],
            'passive': item['passive'],
            'spells': item['spells'],
            'key': item['key']
        }
        output[str(item['id'])] = entry
    return output



def fix_your_spells_rito(spelldata):
    output = {}
    for item in spelldata['data'].values():
        entry = {
            'filename': item['image']['full'],
            'name': item['name'],
            'desc': item['sanitizedDescription']
        }
        output[str(item['id'])] = entry
    return output


def load_match(friendlies, bullies, config):
    friendly_list = []
    bully_list = []
    for item in friendlies:
        friendly_list.append(item['summonerId'])
    for item in bullies:
        bully_list.append(item['summonerId'])
    results = get_league(friendly_list + bully_list, config)
    friendlies = get_stats(friendlies, config, results)
    bullies = get_stats(bullies, config, results)
    masterydata = get_masteries(config)
    runedata = get_runes(config)
    spelldata = fix_your_spells_rito(get_spells(config))
    champdata = fix_your_champs_rito(get_champ(config))
    foutput = sanitisedat(friendlies, runedata, masterydata, spelldata, champdata, config, True)
    boutput = sanitisedat(bullies, runedata, masterydata, spelldata, champdata, config, False)

    return foutput, boutput


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
    con['global'] = 'https://global.api.riotgames.com'
    con['api_key'] = apikey
    con['summoner'] = new_name
    con['region'] = region.lower()
    con['platform'] = endpoints[region]
    con['url'] = 'https://%s.api.pvp.net' % region.lower()
    con['id'] = sumdata[
        ''.join(c.lower() for c in new_name if not c.isspace())]['id']
    con['version'] = get_version(con)
    return con


def get_data(url, argtings, recursion = 5):
    """Retrieves data from url using selected arguments"""
    if recursion == 0:
        print("SYSTEM ERROR")
        return None
    response = requests.get(url % argtings)
    if response.status_code == 404 or response.status_code == 403:
        return None
    if response.status_code == 429:
        for i in range(10):
            time.sleep(1)
        return get_data(url, argtings, recursion=recursion-1)
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


def get_champ(config):
    """retrieves static champion data"""
    data = get_data('%s/api/lol/static-data/%s/v1.2/champion?champData=allytips,enemytips,passive,image,spells&api_key=%s',  # NOQA
                    (config['global'],
                     config['region'],
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
    data = get_data('%s/api/lol/static-data/%s/v1.2/rune?runeListData=image,sanitizedDescription,stats,tags&api_key=%s',  # NOQA
                    (config['global'],
                     config['region'],
                     config['api_key']))
    return data


def get_spells(config):
    """retrieve static spell data"""
    data = get_data('%s/api/lol/static-data/%s/v1.2/summoner-spell?spellData=image,sanitizedDescription&api_key=%s',  # NOQA
                    (config['global'],
                     config['region'],
                     config['api_key']))
    return data


if __name__ == "__main__":
    import os
    key = os.environ.get('rito_api_key')
    config = get_config("WoodDivisionSupp", "EUW", key)
    match = get_match(config, test=True)
    dats = load_match(match[0], match[1], config)
    x = {
        "Friends": dats[0],
        "Bullies": dats[1]
    }
    filename = open("refined_testdata.json", "w")
    json.dump(x, filename)
    filename.close()
    #parse_runes("+4.5% attack speed", 9)
