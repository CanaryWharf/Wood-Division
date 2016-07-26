from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, RiseInTransition, FallOutTransition  # NOQA
from kivy.uix.label import Label  # NOQA
from kivy.uix.button import Button  # NOQA
from kivy.uix.boxlayout import BoxLayout  # NOQA
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput  # NOQA
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
import queue
import threading
import simplejson as json
import re
import backend
from pprint import pprint  # NOQA
ddragon = None


class Heading(Label):
    pass


class ErrorPopup(Popup):
    pass


class StandardLabel(Label):
    pass


class RegionButton(Button):
    pass


class RegionPopup(Popup):
    pass


class nuBox(ButtonBehavior, BoxLayout):
    pass


class ScrollBox(GridLayout):
    pass


class Portrait(AsyncImage):
    pass


class Scroller(ScrollView):
    pass


class MoreInfo(Carousel):

    def __init__(self, info, **kwargs):
        super(MoreInfo, self).__init__(**kwargs)
        self.add_widget(self.champion_page(info['sid'], info['champ']))
        self.add_widget(self.masteries_page(info['masteries']))
        self.add_widget(self.rune_page(info['runes']))

    def champion_page(self, sid, clist):
        view = Scroller()
        box = ScrollBox()
        profile = BoxLayout(orientation='horizontal')
        profile.add_widget(Portrait(
            source='http://ddragon.leagueoflegends.com/cdn/%s/img/champion/%s.png' % (ddragon, clist['key']), size_hint_x=0.3))  # NOQA
        topbox = BoxLayout(orientation='vertical')
        topbox.add_widget(Heading(text=clist['name']))
        results = backend.get_champ_mastery(sid, clist['id'])
        if results:
            mastery = results['championLevel']
        else:
            mastery = 'Absolute Scrublord'
        topbox.add_widget(Heading(text='Level %d' % mastery))
        profile.add_widget(topbox)
        box.add_widget(profile)
        passive = BoxLayout(orientation='vertical')
        passive.add_widget(Portrait(
            source='http://ddragon.leagueoflegends.com/cdn/%s/img/passive/%s' % (ddragon, clist['passive']['image']['full']), size_hint_x=0.3))  # NOQA
        passive.add_widget(StandardLabel(
            text=clist['passive']['sanitizedDescription']))
        for item in clist['spells']:
            sanitised = self.sanitise(item)
            b = BoxLayout(orientation='horizontal')
            b.add_widget(Portrait(
                source='http://ddragon.leagueoflegends.com/cdn/%s/img/spell/%s' % (ddragon, item['image']['full']), size_hint_x=0.3))  # NOQA
            b.add_widget(StandardLabel(text=sanitised))
            box.add_widget(b)

        btn = Button(text='Back')
        btn.bind(on_press=self.back_button)
        box.add_widget(btn)
        view.add_widget(box)
        return view

    def rune_page(self, runelist):
        view = Scroller()
        runes = backend.get_runes()
        box = ScrollBox()
        box.add_widget(Heading(text='Runes'))

        for item in runelist:
            slot = BoxLayout(orientation='horizontal')
            slot.add_widget(Portrait(
                source='http://ddragon.leagueoflegends.com/cdn/%s/img/rune/%s' % (ddragon, runes['data'][  # NOQA
                    str(item['runeId'])]['image']['full'])))
            details = runes['data'][
                str(item['runeId'])]['description']
            desc = self.rune_calculate(details, item['count'])
            slot.add_widget(StandardLabel(text=desc))
            box.add_widget(slot)

        btn = Button(text='Back')
        btn.bind(on_press=self.back_button)
        box.add_widget(btn)
        view.add_widget(box)
        return view

    def masteries_page(self, masterylist):
        view = Scroller()
        masteries = backend.get_masteries()
        box = ScrollBox()
        box.add_widget(Heading(text='Masteries'))
        for item in masterylist:
            slot = BoxLayout(orientation='horizontal')
            slot.add_widget(Portrait(
                source='http://ddragon.leagueoflegends.com/cdn/%s/img/mastery/%s' % (ddragon, masteries['data'][  # NOQA
                    str(item['masteryId'])]['image']['full'])))
            details = masteries['data'][
                str(item['masteryId'])]['description'][item['rank']-1]
            slot.add_widget(StandardLabel(text=details))
            box.add_widget(slot)

        btn = Button(text='Back')
        btn.bind(on_press=self.back_button)
        box.add_widget(btn)
        view.add_widget(box)

        return view

    def rune_calculate(self, desc, count):
        regex = re.compile(r'["+"-]([0-9]+["."]?[0-9]*)\%?\s[a-z\s\/1-9"."]*\(?(["+"-][0-9]+["."]?[0-9]*)?\%?\s?[a-z\s\/1-9"."]*')  # NOQA
        mo = re.findall(regex, desc)
        replacements = {}
        for item in mo:
            replacements[item[0]] = "%.2f" % (float(item[0])*count)
        ans = self.scalings(replacements, desc)
        return ans

    def sanitise(self, spell):
        regex = r'(\{\{.[aef][0-9].\}\})'
        mo = re.findall(regex, spell['sanitizedTooltip'])
        replacements = {}
        for item in mo:
            key = item[3] + item[4]
            if key[0] == 'e':
                replacements[item] = spell['effectBurn'][int(key[1])]
            else:
                if 'vars' in spell:
                    for x in spell['vars']:
                        if x['key'] == key:
                            replacements[item] = str(x['coeff'][0]) + ' ' + x['link']  # NOQA
                            break
                        replacements[item] = 'Rito pls'
                else:
                    replacements[item] = 'Rito pls'
        output = spell['sanitizedTooltip']
        return self.scalings(replacements, output)

    def back_button(self, btn):
        App.get_running_app().root.transition = FallOutTransition()
        App.get_running_app().root.current = 'info_screen'

    def scalings(self, dic, text):
        reg = re.compile("(%s)" % "|".join(map(re.escape, dic.keys())))

        return reg.sub(lambda mo: dic[mo.string[mo.start():mo.end()]], text, 1)


class InfoMenu(Carousel):
    used_screens = ListProperty(None)

    def __init__(self, bully, friend, **kwargs):
        super(InfoMenu, self).__init__(**kwargs)
        self.add_widget(self.get_layout(bully, 'Bullies'))
        self.add_widget(self.get_layout(friend, 'Friends'))
        App.get_running_app().root.get_screen('info_screen').add_widget(self)

    def get_layout(self, roster, team):
        b = BoxLayout(orientation='vertical')
        b.add_widget(StandardLabel(text=team, size_hint=(1, 0.2)))
        for item in roster:
            entry = nuBox(orientation='horizontal',
                          padding=[1, 5],
                          size_hint=(1, 0.6))
            entry.add_widget(AsyncImage(
                source='http://ddragon.leagueoflegends.com/cdn/%s/img/champion/%s' % (ddragon, item['champ']['image']['full']), size_hint=(0.2, 1)))  # NOQA
            labels = BoxLayout(orientation='vertical', size_hint=(0.6, 1))
            if 'division' in item.keys():
                labels.add_widget(StandardLabel(text=item['division']))
                w, l = item['wins'], item['losses']
                if l == 0:
                    divisor = 1
                else:
                    divisor = l
                labels.add_widget(StandardLabel(
                    text='%.2f (%dW, %dL)' % (w/divisor, w, l)))
            else:
                labels.add_widget(StandardLabel(text='Scrub'))
            entry.add_widget(labels)
            entry.memory = item
            entry.bind(on_press=self.get_more_info)
            b.add_widget(entry)
            btn = Button(text='Back', font_size=25, size_hint=(1, 0.2))
            btn.bind(on_release=self.exit_screen)
        b.add_widget(btn)
        return b

    def exit_screen(self, btn):
        self.parent.remove_widget(self)
        self.clear_widgets()
        for item in self.used_screens:
            App.get_running_app().root.remove_widget(
                App.get_running_app().root.get_screen(item))
        App.get_running_app().root.transition = FallOutTransition()
        App.get_running_app().root.current = 'main_screen'

    def get_more_info(self, info):
        if not App.get_running_app().root.has_screen(info.memory['sid']):
            sc = Screen(name=info.memory['sid'])
            m = MoreInfo(info.memory)
            sc.add_widget(m)
            App.get_running_app().root.add_widget(sc)
            self.used_screens.append(info.memory['sid'])
        App.get_running_app().root.transition = RiseInTransition()
        App.get_running_app().root.current = info.memory['sid']


class ConfigMenu(GridLayout):
    name = StringProperty(None)
    region = StringProperty(None)
    pop = ObjectProperty(None)
    endpoints = ListProperty(['BR', 'EUNE', 'EUW', 'JP', 'KR',
                              'LAN', 'LAS', 'NA', 'OCE', 'TR',
                              'RU', 'PBE'])
    err_pop = ObjectProperty(None)
    loading = ObjectProperty(None)
    q = queue.Queue()

    def __init__(self, **kwargs):
        super(ConfigMenu, self).__init__(**kwargs)
        filename = open('config.json')
        conf = json.load(filename)
        filename.close()
        self.name = conf['summoner']
        self.region = conf['region'].upper()
        self.pop = Popup(size_hint=(0.7, 0.7))
        box = BoxLayout(orientation='vertical')
        for item in self.endpoints:
            btn = RegionButton(text=item)
            btn.bind(on_release=self.set_region)
            box.add_widget(btn)
        self.pop.add_widget(box)

    def set_region(self, regbut):
        self.region = regbut.text
        self.pop.dismiss()

    def save_changes(self, namtext):
        self.loading = Popup(title='please wait',
                             size_hint=(0.7, 0.7),
                             auto_dismiss=False,
                             content=Label(text='Processing'))
        self.loading.open()
        changes = threading.Thread(target=self.set_name,
                                   args=(namtext,))
        changes.start()

    def set_name(self, namtext):
        self.name = namtext.text
        result = backend.change_name(self.name, self.region)
        # self.loading.dismiss()
        if result:
            self.back_to_main()
        else:
            self.err_pop = ErrorPopup()
            self.err_pop.open()

    def back_to_main(self):
        App.get_running_app().root.transition = FallOutTransition()
        App.get_running_app().root.current = 'main_screen'


class MainMenu(BoxLayout):

    pop = ObjectProperty(None)
    err_pop = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        global ddragon
        ddragon = backend.get_version()
        self.pop = Popting()
        if ddragon is None:
            self.pop.open()

    def lookup(self):
        try:
            friendlies, bullies = backend.get_match(test=True)
        except TypeError:
            self.pop.open()
            return
        summ_list = []
        friendly_team = friendlies[0]['teamId']
        for item in friendlies + bullies:
            summ_list.append(item['summonerId'])
        league_info = backend.get_league(summ_list)
        friend_list, bully_list = [], []
        for item in friendlies + bullies:
            op = {}
            sid = str(item['summonerId'])
            op['name'] = item['summonerName']
            op['sid'] = sid
            op['champId'] = item['championId']
            if sid in league_info:
                op['wins'] = league_info[sid]['entries'][0]['wins']
                op['losses'] = league_info[sid]['entries'][0]['losses']
                op['division'] = '%s %s' % (
                    league_info[sid]['tier'],
                    league_info[sid]['entries'][0]['division'])
            op['champ'] = backend.get_champ(item['championId'])
            op['runes'] = item['runes']
            op['masteries'] = item['masteries']
            if item['teamId'] == friendly_team:
                friend_list.append(op)
            else:
                bully_list.append(op)
        self.reset_transition()
        self.build_list(bully_list, friend_list)

    def reset_transition(self):
        App.get_running_app().root.transition = RiseInTransition()

    def build_list(self, bully, friend):
        InfoMenu(bully, friend)
        App.get_running_app().root.current = 'info_screen'


class Popting(Popup):
    pass


class MainScreen(Screen):
    pass


class ConfigScreen(Screen):
    pass


class InfoScreen(Screen):
    pass


class MoreInfoScreen(Screen):
    pass


class Screener(ScreenManager):
    pass


class WoodApp(App):
    def build(self):
        s = Screener(transition=RiseInTransition())
        return s

if __name__ == "__main__":
    WoodApp().run()
