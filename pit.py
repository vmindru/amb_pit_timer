#!/usr/bin/env python
from kivy.app import App
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.animation import Animation


Builder.load_string('''

<RootWidget>:
    #:import randint  random.randint
    #:import get_color_from_hex kivy.utils.get_color_from_hex
    orientation: "vertical"
    BoxLayout:
        orientation: "vertical"
        CountDownLbl:
            bg_color: 1,0,0
            timer_duration: 1
            markup: True
            id: anim_label
            font_size: 30
            text: "[color={}]Kart1[/color] \\n [color={}]{}.000[/color]".format(self.Green, self.Red, self.timer_duration)
            canvas:
                Color:
#                    rgb: get_color_from_hex(self.Green) if self.in_progress else get_color_from_hex(self.Red)
                    rgb: get_color_from_hex(self.Yellow)
                Line:
                    circle:self.center_x, self.center_y, 90
                    width: 15
        CountDownLbl:
            bg_color: 1,0,0
            timer_duration: 1
            markup: True
            id: anim_label2
            font_size: 30
            text: "[color={}]Kart1[/color] \\n [color={}]{}.000[/color]".format(self.Green, self.Red, self.timer_duration)
            canvas:
                Color:
#                    rgb: get_color_from_hex(self.Yellow) if self.in_progress else get_color_from_hex(self.Yellow)
                    rgb: get_color_from_hex(self.Yellow)
                Line:
                    circle:self.center_x, self.center_y, 90
                    width: 15
    BoxLayout:
        o1rientation: "horizontal"
        Button:
            size_hint_y: 0.1
            text: "Start"
            on_press: anim_label.start()

        Button:
            size_hint_y: 0.1
            text: "Start"
            on_press: anim_label2.start()
        ''')


class RootWidget(BoxLayout):
    pass


class SecondLabel(Label):
    pass


class CountDownLbl(Label):
    Yellow = "#F9F900"
    Red = "F90000"
    Green = "41FD00"
    bg_color = get_color_from_hex(Red)
    angle = NumericProperty(0)
    timer_duration = NumericProperty(0)

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

    def finish(self, animation, widget):
        widget.text = "[color={}]Kart1[/color] \n [color={}] GO!!!! [/color]".format(self.Green, self.Green)
        self.in_progress = False

    def update_timer(self, animation, widget, progression):
        text = ((self.timer_duration * 60000)*(1-progression))/60000
        widget.text = "[color={2}]Kart1[/color] \n [color={1}]{0:.3f}[/color]".format(float(text), self.Red, self.Green)


class TestApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    TestApp().run()
