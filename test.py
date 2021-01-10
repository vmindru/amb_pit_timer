#!/usr/bin/env python
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.animation import Animation
from kivy.config import Config

Config.set('modules', 'random', '')

Builder.load_string('''

<RootWidget>:
    #:import randint  random.randint
    orientation: "vertical"
    CountDownLbl:
        id: anim_label
        text: "{0:.3f}".format(float(self.startCount - self.angle / 360))
        font_size: 30
        canvas:
            Color:
                rgb: randint(1,10),randint(1,10),randint(1,10)
            Line:
                circle:self.center_x, self.center_y, 90, 0, self.angle % 360
                width: 5
    Button:
        size_hint_y: 0.1
        text: "Start"
        on_press: anim_label.start()
        ''')

COUNT = 2


class RootWidget(BoxLayout):
    pass


class CountDownLbl(Label):
    startCount = COUNT
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CountDownLbl, self).__init__(**kwargs)

    def start(self):
        self.startCount = COUNT
        print(dir(self.canvas))
        print(dir(RootWidget))
        self.anim = Animation(angle=360 * self.startCount,  duration=self.startCount)
        self.anim.bind(on_complete=self.finish)
        self.anim.start(self)

    def finish(self, animation, incr_crude_clock):
        CountDownLbl.startCount = COUNT
        incr_crude_clock.text = "FINISHED"


class TestApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    TestApp().run()
