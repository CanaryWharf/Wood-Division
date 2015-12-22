from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button  # NOQA
from kivy.uix.textinput import TextInput  # NOQA
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty  # NOQA
from kivy.properties import NumericProperty  # NOQA
import simplejson as json
import backend  # NOQA

infoscreens = []


class Popting(Popup):
    pass


class InfoMenu(BoxLayout):
    pop = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(InfoMenu, self).__init__(**kwargs)

    def show_info(self, lane):
        grid = LaneInfo(lane)
        grid.list_data()
        grid.bind(minimum_height=grid.setter('height'))
        gridroot = ScrollView()
        gridroot.add_widget(grid)
        self.pop = Popting(title='Play Info', content=gridroot)
        self.pop.open()


class InfoScreen(Screen):
    pass


class InfoBlock(Label):
    pass


class LaneInfo(GridLayout):
    info = None
    lane = None

    def __init__(self, lane, **kwargs):
        super(LaneInfo, self).__init__(**kwargs)
        self.lane = lane

    def list_data(self):
        global infoscreens
        self.info = infoscreens[self.lane]
        for key in self.info.keys():
            self.add_widget(InfoBlock(text=key))
            self.add_widget(InfoBlock(text=json.dumps(self.info[key])))


class MainMenu(BoxLayout):

    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)

    def gendata(self):
        global infoscreens
        self.ids['run_button'].text = 'Processing...\nPlease wait'
        infoscreens = backend.run(test=True)


class MainScreen(Screen):
    pass


class Screener(ScreenManager):
    pass


class WoodApp(App):
    def build(self):
        return Screener()


if __name__ == "__main__":
    WoodApp().run()
