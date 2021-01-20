#!/usr/bin/env python
from kivy.app import App
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.animation import Animation


Builder.load_string('''

<KartTimer@Timer>:
    id: kart_timer
    kart_number: 0
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
        orientation: 'vertical'
        KartTimer:
            kart_number: 1
        KartTimer:
            kart_number: 2
        KartTimer:
            kart_number: 3
        KartTimer:
            kart_number: 4
        KartTimer:
            kart_number: 5
        KartTimer
            kart_number: 6
        ''')


class RootWidget(BoxLayout):
    def on_released(self):
        self.add_widget(KartTimer())
    pass


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
            self.anim = Animation(angle=360 * self.anim_duration,  duration=self.timer_duration)
            self.in_progress = True
            self.anim.bind(on_complete=self.finish, on_progress=self.update_timer)
            self.anim.start(self)

    def update_timer_value(self, value):
        if not self.in_progress:
            try:
                value = int(value)
                print(self.timer_duration)
                self.timer_duration = value
                print(self.timer_duration)
            except ValueError as E:
                print("{} is not int".format(E))

    def stop(self):
        print(len(self.parent.parent.parent.children))
        print(self.parent.parent.parent.children)
        print(self.parent.parent.children)
        if hasattr(self, 'anim'):
            self.anim.stop(self)

    def finish(self, animation, widget):
        widget.text = "{}[color={}] GO!!!! [/color]".format(self.kart_text, self.Green)
        self.in_progress = False

    def update_timer(self, animation, widget, progression):
        text = ((self.timer_duration * 60000)*(1-progression))/60000
        widget.text = "{1}[color={2}]{0:.3f}[/color]".format(float(text), self.kart_text, self.Red)



class TestApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    TestApp().run()
