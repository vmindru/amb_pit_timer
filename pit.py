#!/usr/bin/env python
from kivy.support import install_twisted_reactor
import sys
if 'twisted.internet.reactor' in sys.modules:
    del sys.modules['twisted.internet.reactor']
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
from kivy.clock import Clock
from AmbP3.decoder import Connection.split_
from AmbP3.decoder import p3decode


import yaml


KART_NUMBERS_FILE = 'kart_numbers.yaml'
MAIN_CONFIG = 'pit_config.yaml'
DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT_START = 12001
DEFAULT_PORT_FINISH = 12002
DEFAULT_DUAL_MODE = False
DEFAULT_TIMER_DURATION = 30

Builder.load_file("pit_layout.kv")


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
            parent.add_widget(child, index=(len(children)-1))
            child.children[0].children[0].start()

    def print_message(self, data):
        print(data)

    def split_records(self, data):
        """some times server send 2 records in one message
           concatinated, you can find those by '8f8e' EOR and SOR next to eahc other"""
        byte_array = bytearray(data)
        size = len(byte_array)
        split_data = [bytearray()]
        for index, byte in enumerate(byte_array):
            if index != size-1 and byte == 143 and byte_array[index+1] == 142:
                logger.debug("found delimeter byte 143,142 b'8f8e'")
                split_data[-1].append(byte)
                split_data.append(bytearray())
                logger.debug("start new record")
            else:
                split_data[-1].append(byte)
        return split_data

    def process_message(self, data):
        for msg in split_records(self, data):
            decoded_header, decoded_body = p3decode(msg)
            print("RECIVED: {}, {}".format(decoded_header,decoded_body))
            if 'TOR' in decoded_body['RESULT']:
                if 'PASSING' in decoded_body['RESULT']['TOR']:
                    transponder = int(decoded_body['RESULT']['TRANSPONDER'].decode(), 16)
                    self.start(transponder)

    def connect_to_server(self):
        reactor.connectTCP(IP_START, PORT_START, AmbClientFactory(self))
        if DUAL_MODE:
            reactor.connectTCP(IP_FINISH, PORT_FINISH, AmbClientFactory(self))

class Timer(BoxLayout):
    kart_number: NumericProperty(0)
    pass


class SecondLabel(Label):
    pass


class CountDownLbl(Label):
    kart_number: NumericProperty(0)
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


    def get_default_timer(self):
        return TIMER_DURATION

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
                self.update_timer_value(self.get_default_timer())
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


class PitTimerApp(App):
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
        self.app.print_message('Lost connection for {}:{} with state: {}'.format(connector.host, connector.port, connector.state))
        Clock.schedule_once(lambda dt: connector.connect() , 1)

    def clientConnectionFailed(self, connector, reason):
        self.app.print_message('Connection failed for {}:{} with state: {}'.format(connector.host, connector.port, connector.state))
        Clock.schedule_once(lambda dt: connector.connect() , 1)



def main():
    global IP_START, PORT_START, IP_FINISH, PORT_FINISH, DUAL_MODE, KART_NUMBERS, TIMER_DURATION
    KART_NUMBERS = read_yaml_config(KART_NUMBERS_FILE)
    CONFIG = read_yaml_config(MAIN_CONFIG)
    IP_START = CONFIG['IP_START'] if 'IP_START' in CONFIG else DEFAULT_IP
    PORT_START = CONFIG['PORT_START'] if 'PORT_START' in CONFIG else DEFAULT_PORT_START
    IP_FINISH =  CONFIG['IP_FINISH'] if 'IP_FINISH' in CONFIG else DEFAULT_IP
    PORT_FINISH = CONFIG['PORT_FINISH'] if 'PORT_FINISH' in CONFIG else DEFAULT_PORT_FINISH
    DUAL_MODE = CONFIG['DUAL_MODE'] if 'DUAL_MODE' in CONFIG else DEFAULT_DUAL_MODE
    TIMER_DURATION = CONFIG['TIMER_DURATION'] if 'TIMER_DURATION' in CONFIG  else DEFAULT_TIMER_DURATION
    PitTimerApp().run()


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
