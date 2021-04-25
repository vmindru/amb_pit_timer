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
# from AmbP3.decoder import Connection
from AmbP3.decoder import p3decode

import yaml


KART_NUMBERS_FILE = 'kart_numbers.yaml'
MAIN_CONFIG = 'demo_server_config.yaml'
DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT_START = 12001
DEFAULT_PORT_FINISH = 12002
DEFAULT_DUAL_MODE = False
DEFAULT_TIMER_DURATION = 33

Builder.load_file("demo_server_layout.kv")


class RootWidget(BoxLayout):

    def __init__(self):
        self.start_listening()
        super(RootWidget, self).__init__()

    def print_message(self, data):
        print(data)

    def process_message(self, data):
        decoded_header, decoded_body = p3decode(data)
        print(decoded_header, decoded_body)
        if 'TOR' in decoded_body['RESULT']:
            if 'PASSING' in decoded_body['RESULT']['TOR']:
                transponder = int(decoded_body['RESULT']['TRANSPONDER'].decode(), 16)
                self.start(transponder)

    def start_listening(self):
        reactor.listenTCP(PORT_START, AmbServerFactory(self))
        reactor.listenTCP(PORT_FINISH, AmbServerFactory(self))






class Kart(BoxLayout):

    def send_start(self):
        transponder_id = self.children[0].children[0].children[0].text
        MSG = "Sending start for {}".format(transponder_id)
        print(MSG)
        print(dir(reactor))





    def send_finish(self):
        transponder_id = self.children[0].children[0].children[0].text
        print("Sending finish for {}".format(transponder_id))
    pass


class KartSend(Label):
    transponder_id: NumericProperty(0)
    Yellow = "#F9F900"
    Red = "F90000"
    Green = "41FD00"
    bg_color = get_color_from_hex(Red)


    def __init__(self, **kwargs):
        super(CountDownLbl, self).__init__(**kwargs)
        self.anim_duration = self.timer_duration
        self.in_progress = False


    def get_default_timer(self):
        return TIMER_DURATION

    def update_timer_value(self, value):
        if not self.in_progress:
            try:
                value = int(value)
                self.timer_duration = value
                self.parent.children[1].children[0].text = str(value)
                self.parent.children[1].children[0].cursor = (len(self.parent.children[1].children[0].text),1)
            except ValueError as E:
                self.update_timer_value(self.get_default_timer())
                self.parent.children[1].children[0].cursor = (len(self.parent.children[1].children[0].text),1)
                print("{} is not int".format(E))



    def finish(self, animation, widget):
        widget.text = "{}[color={}] GO!!!! [/color]".format(self.kart_text, self.Green)
        self.in_progress = False
        self.update_timer_value(self.get_default_timer())


    def update_timer(self, animation, widget, progression):
        text = ((self.timer_duration * 60000) * (1 - progression)) / 60000
        widget.text = "{1}[color={2}]{0:.1f}[/color]".format(float(text), self.kart_text, self.Red)


class DemoServerApp(App):
    def build(self):
        return RootWidget()



class AmbServer(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.getHost()
        self.factory.conn.sendData(data)

    def sendData(self):
        self.transport.write("data")




class AmbServerFactory(protocol.Factory):
    def __init__(self, app):
        self.app = app

    def buildProtocol(self, *args, **kwargs):
        if self.counter == self.MAX_CLIENT:
            return None
        self.counter += 1
        protocol = AmbServer(app)
        protocol.factory = self
        protocol.factory.clients = []
        return protocol




def main():
    global IP_START, PORT_START, IP_FINISH, PORT_FINISH, DUAL_MODE, KART_NUMBERS, TIMER_DURATION
    KART_NUMBERS = read_yaml_config(KART_NUMBERS_FILE)
    CONFIG = read_yaml_config(MAIN_CONFIG)
    print(CONFIG)
    IP_START = CONFIG['IP_START'] if 'IP_START' in CONFIG else DEFAULT_IP
    PORT_START = CONFIG['PORT_START'] if 'PORT_START' in CONFIG else DEFAULT_PORT_START
    IP_FINISH =  CONFIG['IP_FINISH'] if 'IP_FINISH' in CONFIG else DEFAULT_IP
    PORT_FINISH = CONFIG['PORT_FINISH'] if 'PORT_FINISH' in CONFIG else DEFAULT_PORT_FINISH
    DUAL_MODE = CONFIG['DUAL_MODE'] if 'DUAL_MODE' in CONFIG else DEFAULT_DUAL_MODE
    TIMER_DURATION = CONFIG['TIMER_DURATION'] if 'TIMER_DURATION' in CONFIG else DEFAULT_TIMER_DURATION
    DemoServerApp().run()


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
