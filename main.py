from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label  # NOQA
from kivy.uix.button import Button  # NOQA
from kivy.uix.boxlayout import BoxLayout  # NOQA
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput  # NOQA
from kivy.properties import StringProperty
import simplejson as json
import backend


class StandardLabel(Label):
    pass


class ConfigMenu(GridLayout):
    name = StringProperty(None)
    region = StringProperty(None)
    new_name = StringProperty(None)
    pop = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ConfigMenu, self).__init__(**kwargs)
        filename = open('config.json')
        conf = json.load(filename)
        filename.close()
        self.name = conf['summoner']
        self.region = conf['region'].upper()


class MainMenu(BoxLayout):

    pop = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        self.pop = Popting()


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
        s = Screener()
        return s

if __name__ == "__main__":
    WoodApp().run()
