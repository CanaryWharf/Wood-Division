# Main project

import simplejson as json
import requests
import sys
import os
import bs4
import threading
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
screendict = {}


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
    try:
        dic = get_data(
            '%s/api/lol/euw/v1.4/summoner/by-name/%s?api_key=%s', (url,
                                                                   name,
                                                                   api_key))
    except requests.exceptions.HTTPError:
        sys.exit('Name not found')
    print(dic)
    id = dic[list(dic.keys())[0]]['id']
    try:
        dic = get_data(
            '%s/observer-mode/rest/consumer/getSpectatorGameInfo/%s/%s?api_key=%s',  # NOQA
            (url, server, id, api_key))
    except requests.exceptions.HTTPError:
        sys.exit('Game not found. Is player in a game?')
    fat = dic['participants']
    if len(fat) != 10:
        sys.exit('Program currently only supports Summoner\'s rift')
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


def lane(play_info, team):
    posfile = open('champ_pos.json', 'r')
    pos = json.load(posfile)
    posfile.close()
    positions = {}
    remainder = ['Top', 'Mid', 'Bottom', 'Bottom', 'Jungler']
    champs = []
    for item in play_info:
        if item['spells'][0] == 'Smite' or item['spells'][1] == 'Smite':  # NOQA
            positions[item['champ']] = 'Jungler'
            if 'Jungler' not in remainder:
                for x in positions:
                    if positions[x] == 'Jungler':
                        positions[x] = ''
                        remainder.append('Jungler')
                        remainder.append('Jungler')
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
        if count > 6:
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
            for item in rejects[key]:
                if item in current_count.keys():
                    current_count[item] += 1
                else:
                    current_count[item] = 1
        for key in current_count:
            if current_count[key] == 1:
                for val in rejects:
                    if key in rejects[val]:
                        positions[val] = key
                        rejects.pop(val)
                        try:
                            remainder.remove(key)
                        except ValueError:
                            pass
                        break
    while remainder:
        print('Unknown Positions')
        for key in rejects:
            print(key)
            nums = len(rejects[key])
            for x in range(nums):
                print('%d: %s (%s)' % (x+1, rejects[key][x], team))
            try:
                ans = int(input('>'))
                positions[key] = rejects[key][ans-1]
                remainder.remove(rejects[key][ans-1])
            except ValueError:
                pass

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
    try:
        data = get_data(
            '%s/api/lol/%s/v1.3/stats/by-summoner/%s/ranked?api_key=%s',
            (url, region, sid, api_key))
    except requests.exceptions.HTTPError:
        return {'Total Scrub': 'Never played Ranked'}
        return 0
    c = data['champions']
    stats = {}
    for item in c:
        if item['id'] == cid:
            stats = item['stats']
            break
    if not stats:
        return {'Cherry Popped': 'No ranked games played with Champion'}
        return 0
    else:
        if stats['totalDeathsPerSession'] == 0:
            stats['totalDeathsPerSession'] = 1
        if stats['totalSessionsPlayed'] == 0:
            stats['totalSessionsPlayed'] = 1
        if stats['totalSessionsLost'] == 0:
            stats['totalSessionsLost'] = 1
        return {'KDA': '%.2f' % (stats['totalChampionKills']/stats['totalDeathsPerSession']),  # NOQA
                'Avg Assists': '%.2f' % (stats['totalAssists']/stats['totalSessionsPlayed']),  # NOQA
                'W/L': '%.2f' % (stats['totalSessionsWon']/stats['totalSessionsLost']),  # NOQA
                'Played': str(stats['totalSessionsPlayed'])}


def counter_rating(friend, bully):
    soup = get_soup('http://www.lolcounter.com/champions/%s/weak',
                    (bully))
    weak = soup.select('.weak-block .name')
    for item in weak:
        if item.getText() == friend:
            return 0
    soup = get_soup('http://www.lolcounter.com/champions/%s/strong',
                    (bully))
    strong = soup.select('.weak-block .name')
    for item in strong:
        if item.getText() == friend:
            return 2
    return 1


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
    if not spectips:
        spectips = gentips
    return gentips, spectips


def matchup(friend, bully):
    levels = ['Green', 'Yellow', 'Red']
    if len(friend) == 2:
        Dang = levels[int(sum([counter_rating(friend[0], bully[0]),
                               counter_rating(friend[0], bully[1]),
                               counter_rating(friend[1], bully[0]),
                               counter_rating(friend[1], bully[1])]) / 4)]
        tips = [{friend[0]: {bully[0]: counter_tips(friend[0], bully[0]),
                             bully[1]: counter_tips(friend[0], bully[1])}},
                {friend[1]: {bully[0]: counter_tips(friend[1], bully[0]),
                             bully[1]: counter_tips(friend[1], bully[1])}}]
        gentips = []
        spectips = []
        for item in tips:
            gentips.append(item)
            spectips.append(item)
    else:
        Dang = levels[counter_rating(friend[0], bully[0])]
        gentips, spectips = counter_tips(friend[0], bully[0])
    return Dang, gentips, spectips


def lane_match(friends, bullies, lane):
    f1 = []
    b1 = []
    for key in bullies:
        if bullies[key] == lane:
            x = None
            for y in friends:
                if friends[y] == lane:
                    x = y
                    friends.pop(x)
                    break
            f1.append(x)
            b1.append(key)
    return f1, b1


def screengen(f1, b1, lane):
    screen = {}
    f2, b2 = lane_match(f1, b1, lane)
    dang, gentips, spectips = matchup(f2, b2)
    screen['Danger'] = dang
    screen['General'] = gentips
    if gentips != spectips:
        screen['Special'] = spectips
    screendict[lane] = screen
    print('%s research complete.' % (lane))


def screen_select(screens):
    pos = ['Top', 'Mid', 'Bot', 'Jungle']
    print(screens[3]['Danger-levels'])
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Select Screen')
        for x in range(4):
            print('%d: %s' % (x+1, pos[x]))
        print('5: Exit')
        ans = int(input('>'))
        if ans == 5:
            break
        # pprint(screens[ans-1])
        input('Enter to go back:')


def find_rating(bullies, b1, lane):
    for key in b1:
        if b1[key] == lane:
            for item in bullies:
                if item['champ'] == key:
                    screendict[lane + ' KDA'] = player_info(item['id'],
                                                            item['champ_id'])


def run(test=True):
    print('Looking up game: %s...' % (summoner))
    if test:
        skim = tester()
    else:
        skim = match_data(summoner)
    print('Sorting teams...')
    friendlies, bullies = teams(skim)
    bull_lane = lane(bullies, 'Bully')
    friend_lane = lane(friendlies, 'Friend')
    print('Conducting Research...')
    topthread1 = threading.Thread(target=screengen,
                                  args=(friend_lane, bull_lane, 'Top'))
    topthread1.start()
    topthread2 = threading.Thread(target=find_rating,
                                  args=(bullies, bull_lane, 'Top'))
    topthread2.start()
    midthread1 = threading.Thread(target=screengen,
                                  args=(friend_lane, bull_lane, 'Mid'))
    midthread1.start()
    midthread2 = threading.Thread(target=find_rating,
                                  args=(bullies, bull_lane, 'Mid'))
    midthread2.start()
    botthread1 = threading.Thread(target=screengen,
                                  args=(friend_lane, bull_lane, 'Bottom'))
    botthread1.start()
    botthread2 = threading.Thread(target=find_rating,
                                  args=(bullies, bull_lane, 'Bottom'))
    botthread2.start()
    jungthread1 = threading.Thread(target=screengen,
                                   args=(friend_lane, bull_lane, 'Jungler'))
    jungthread1.start()
    jungthread2 = threading.Thread(target=find_rating,
                                   args=(bullies, bull_lane, 'Jungler'))
    jungthread2.start()
    for item in [topthread1, topthread2,
                 midthread1, midthread2,
                 botthread1, botthread2,
                 jungthread1, jungthread2]:
        item.join()
    print('Generating Screens...')
    topscreen = screendict['Top']
    topscreen['KDA'] = screendict['Top KDA']
    midscreen = screendict['Mid']
    midscreen['KDA'] = screendict['Mid KDA']
    botscreen = screendict['Bottom']
    botscreen['KDA'] = screendict['Bottom KDA']
    jungscreen = screendict['Jungler']
    jungscreen['KDA'] = screendict['Jungler KDA']
    for item in [topscreen, midscreen, botscreen]:
        item['Jungler'] = jungscreen['General']
    jungscreen['Top'] = topscreen['General']
    jungscreen['Danger-levels'] = 'Top: %s, Mid: %s, Bot: %s' % (
        topscreen['Danger'], midscreen['Danger'], botscreen['Danger'])
    jungscreen['Mid'] = midscreen['General']
    jungscreen['Bottom'] = {}
    for item in botscreen['General']:
        for f in item.keys():
            for key in item[f].keys():
                jungscreen['Bottom'][key] = item[f][key][0]
    print('Complete')
    return [topscreen, midscreen, botscreen, jungscreen]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test = True
    else:
        test = False
    screen_select(run(test))
