#!/usr/bin/env python
from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import reactor, protocol

from kivy.app import App
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.animation import Animation
# from kivy.clock import Clock
# from AmbP3.decoder import Connection
from AmbP3.decoder import p3decode

import yaml


KART_NUMBERS_FILE = 'kart_numbers.yaml'
MAIN_CONFIG = 'pit_config.yaml'
DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 12001


Builder.load_string('''

<KartTimer@Timer>:
    id: kart_timer
    kart_number: 0
    transponder: 0
    timer_duration: 30
    GridLayout:
        cols: 2
        row_default_height: 40
        row_default_width: 40
        BoxLayout:
            Button:
                text: "Start"
                on_press: anim_label.start()
            Button:
                text: "Stop"
                on_press: anim_label.stop()
            TextInput:
                id: timer_value
                hint_text: "pit stop time in seconds"
                on_text: anim_label.update_timer_value(self.text)
        CountDownLbl:
            timer_duration: kart_timer.timer_duration
            markup: True
            id: anim_label
            font_size: self.height * 0.6
            kart_number: kart_timer.kart_number
            kart_text: "[color={0}]Kart  {1}[/color] ".format(self.Green, self.kart_number)
            text: "{0}[color={1}]{2}.000[/color]".format(self.kart_text,self.Red,self.timer_duration)
            canvas:
                Color:
                    rgb: get_color_from_hex(self.Yellow)
                Line:
#                    circle:self.center_x, self.center_y, 90
                    rectangle: self.x, self.y, self.width, self.height
                    width: 15

<RootWidget>:
    #:import randint  random.randint
    #:import get_color_from_hex kivy.utils.get_color_from_hex
    BoxLayout:
        id: main_box
        orientation: 'vertical'
        KartTimer:
            kart_number: 1
            transponder: 1
        KartTimer:
            kart_number: 2
            transponder: 5691251
        KartTimer:
            kart_number: 3
            transponder: 3
        KartTimer:
            kart_number: 4
            transponder: 4
        KartTimer:
            kart_number: 5
            transponder: 5
        KartTimer
            kart_number: 6
            transponder: 6
        ''')


class RootWidget(BoxLayout):
    def __init__(self):
        self.connect_to_server()
        super(RootWidget, self).__init__()

    def start(self, transponder):
        parent = self.children[0]
        children = parent.children

        if transponder in KART_NUMBERS:
            kart_number = KART_NUMBERS[transponder]
        else:
            kart_number = transponder
        child_index = 0
        for index, child in enumerate(children):
            if child.kart_number == kart_number:
                child_index = index
        child = children[child_index]
        if not child.children[0].children[0].in_progress:
            child.kart_number = kart_number
            child.transponder = transponder
            parent.remove_widget(child)
            parent.add_widget(child, index=5)
            child.children[0].children[0].start()

    def print_message(self, data):
        print(data)

    def process_message(self, data):
        decoded_header, decoded_body = p3decode(data)
        print(decoded_header, decoded_body)
        if 'TOR' in decoded_body['RESULT']:
            if 'PASSING' in decoded_body['RESULT']['TOR']:
                transponder = int(decoded_body['RESULT']['TRANSPONDER'].decode(), 16)
                self.start(transponder)
        print(self.children)

    def connect_to_server(self):
        reactor.connectTCP(IP, PORT, AmbClientFactory(self))


class Timer(BoxLayout):
    kart_number: NumericProperty(0)
    pass


class SecondLabel(Label):
    pass


class CountDownLbl(Label):
    kartgnumber: NumericProperty(0)
    Yellow = "#F9F900"
    Red = "F90000"
    Green = "41FD00"
    bg_color = get_color_from_hex(Red)
    angle = NumericProperty(0)
    timer_duration = NumericProperty(0)
    kart_text = StringProperty("")

    def __init__(self, **kwargs):
        super(CountDownLbl, self).__init__(**kwargs)
        self.anim_duration = self.timer_duration
        self.in_progress = False

    def start(self):
        if not self.in_progress:
            self.anim_duration += self.timer_duration
            self.anim = Animation(angle=360 * self.anim_duration, duration=self.timer_duration)
            self.in_progress = True
            self.anim.bind(on_complete=self.finish, on_progress=self.update_timer)
            self.anim.start(self)

    def update_timer_value(self, value):
        if not self.in_progress:
            try:
                value = int(value)
                self.timer_duration = value
            except ValueError as E:
                print("{} is not int".format(E))

    def stop(self):
        if hasattr(self, 'anim'):
            self.anim.stop(self)

    def finish(self, animation, widget):
        widget.text = "{}[color={}] GO!!!! [/color]".format(self.kart_text, self.Green)
        self.in_progress = False

    def update_timer(self, animation, widget, progression):
        text = ((self.timer_duration * 60000) * (1 - progression)) / 60000
        widget.text = "{1}[color={2}]{0:.1f}[/color]".format(float(text), self.kart_text, self.Red)


class TestApp(App):
    def build(self):
        return RootWidget()


class AmbClient(protocol.Protocol):
    def connectionMade(self):
        # PROCESS HERE CONNECTION
        pass

    def dataReceived(self, data):
        self.factory.app.process_message(data)


class AmbClientFactory(protocol.ClientFactory):
    protocol = AmbClient

    def __init__(self, app):
        self.app = app

    def startedConnecting(self, connector):
        self.app.print_message('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        self.app.print_message('Lost connection.')

    def clientConnectionFailed(self, connector, reason):
        self.app.print_message('Connection failed.')


def main():
    global IP, PORT, KART_NUMBERS
    KART_NUMBERS = read_yaml_config(KART_NUMBERS_FILE)
    CONFIG = read_yaml_config(MAIN_CONFIG)
    IP = CONFIG['IP'] if 'IP' in CONFIG else DEFAULT_IP
    PORT = CONFIG['PORT'] if 'PORT' in CONFIG else DEFAULT_PORT
    TestApp().run()


def read_yaml_config(YAML_FILE):
    DATA = {}
    try:
        with open(YAML_FILE) as yaml_file:
            DATA = yaml.full_load(yaml_file)
    except IOError:
        print("could not load {}".format(YAML_FILE))
    except yaml.YAMLError:
        print("Failed to read config, something wrong iwth YAML content in {}".foramt(YAML_FILE))
    return DATA


if __name__ == '__main__':
    main()
