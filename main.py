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
from kivy.uix.image import Image
import os
import backend  # NOQA

infoscreens = []


class Popting(Popup):
    pass


class InfoTitle(Label):
    pass


class InfoMenu(BoxLayout):
    pop = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(InfoMenu, self).__init__(**kwargs)

    def show_info(self, lane):
        print(App.get_running_app().root.screen_names)
        lanes = ['Top', 'Mid', 'Bottom', 'Jungler']
        if lanes[lane] not in App.get_running_app().root.screen_names:
            grid = LaneInfo(lane)
            grid.list_data()
            grid.bind(minimum_height=grid.setter('height'))
            gridroot = ScrollView()
            gridbox = BoxLayout(orientation='vertical',
                                padding=[10, 10, 10, 10])
            if lane == 2:
                nubox = BoxLayout(size_hint_y=None)
                img1 = os.path.join('images', grid.champ[0] + '.png')
                img2 = os.path.join('images', grid.champ[1] + '.png')
                nubox.add_widget(Portrait(source=img1))
                nubox.add_widget(Portrait(source=img2))
                gridbox.add_widget(nubox)
            else:
                img = os.path.join('images', grid.champ + '.png')
                gridbox.add_widget(Portrait(source=img))
            gridbox.add_widget(gridroot)
            gridbox.add_widget(Close(lanes[lane]))
            gridroot.add_widget(grid)
            gridscreen = Screen(name=lanes[lane])
            gridscreen.add_widget(gridbox)
            App.get_running_app().root.add_widget(gridscreen)
        App.get_running_app().root.current = lanes[lane]


class Portrait(Image):
    pass


class Close(Button):
    lane = None

    def __init__(self, lane, **kwargs):
        super(Close, self).__init__(**kwargs)

    def on_release(self):
        App.get_running_app().root.current = 'info_screen'


class InfoScreen(Screen):
    pass


class InfoBlock(Label):
    pass


class LaneInfo(GridLayout):
    info = None
    lane = None
    champ = None

    def __init__(self, lane, **kwargs):
        super(LaneInfo, self).__init__(**kwargs)
        self.lane = lane

    def list_data(self):
        global infoscreens
        self.info = infoscreens[self.lane]
        self.champ = self.info['Bully']
        for key in self.info.keys():
            if key == 'Bully':
                continue
            self.add_widget(InfoTitle(text=key))
            self.add_widget(InfoBlock(text=self.famting(self.info[key])))

    def famting(self, datum):
        if isinstance(datum, (str, int, float)):
            return datum
        elif isinstance(datum, dict):
            block = []
            for key in datum:
                block.append('%s: %s' % (key, self.famting(datum[key])))
                block.append('\n')
            return '\n'.join(block)
        else:
            return '\n'.join(self.famting(x) for x in datum)


class MainMenu(BoxLayout):

    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)

    def gendata(self):
        global infoscreens
        infoscreens = backend.run(test=True)


class MainScreen(Screen):
    pass


class Screener(ScreenManager):
    pass


class WoodApp(App):
    def build(self):
        s = Screener()
        return s


if __name__ == "__main__":
    WoodApp().run()
