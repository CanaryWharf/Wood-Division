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
import queue
import threading
import simplejson as json
import backend
from pprint import pprint  # NOQA


class ErrorPopup(Popup):
    pass


class StandardLabel(Label):
    pass


class RegionButton(Button):
    pass


class RegionPopup(Popup):
    pass


class InfoMenu(Carousel):

    def __init__(self, bully, friend, **kwargs):
        super(InfoMenu, self).__init__(**kwargs)
        self.add_widget(self.get_layout(bully, 'Bullies'))
        self.add_widget(self.get_layout(friend, 'Friends'))
        App.get_running_app().root.get_screen('info_screen').add_widget(self)

    def get_layout(self, roster, team):
        b = BoxLayout(orientation='vertical')
        b.add_widget(StandardLabel(text=team))
        for item in roster:
            entry = BoxLayout(orientation='horizontal')
            entry.add_widget(AsyncImage(
                source='http://ddragon.leagueoflegends.com/cdn/5.2.1/img/champion/%s.png' % item['champ']['key']))  # NOQA
            labels = BoxLayout(orientation='vertical')
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
            b.add_widget(entry)
            btn = Button(text='Back', font_size=25)
            btn.bind(on_release=self.exit_screen)
            b.add_wdiget(btn)
        return b

    def exit_screem(self):
        App.get_running_app().root.current = 'main_menu'
        App.get_running_app.root.get_screen('info_screen').clear_widgets()


class ConfigMenu(GridLayout):
    name = StringProperty(None)
    region = StringProperty(None)
    pop = ObjectProperty(None)
    endpoints = ListProperty(['BR', 'EUNE', 'EUW', 'JP', 'KR',
                              'LAN', 'LAS', 'NA', 'OCE', 'TR',
                              'RU', 'PBE'])
    box = ObjectProperty(None)
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
        self.box = BoxLayout(orientation='vertical')
        for item in self.endpoints:
            btn = RegionButton(text=item)
            btn.bind(on_release=self.set_region)
            self.box.add_widget(btn)
        self.pop.add_widget(self.box)

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
    bully_list = ListProperty(None)
    friend_list = ListProperty(None)

    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        self.pop = Popting()

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
            if item['teamId'] == friendly_team:
                self.friend_list.append(op)
            else:
                self.bully_list.append(op)
        self.reset_transition()
        self.build_list(self.bully_list, self.friend_list)

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
