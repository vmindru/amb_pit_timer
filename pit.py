#!/usr/bin/env python
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.animation import Animation


Builder.load_string('''

<Timer@CountDown>:
    orientation: "horizontal"
    id: count_down
    timer_duration: 0
    BoxLayout:
        orientation: "vertical"
        Button:
            id: "button_{}".format(timer.id)
            size_hint_y: 0.1
            text: "Start"
            on_press: anim_label.start()
    CountDownLbl:
        timer_duration: count_down.timer_duration
        id: anim_label
        font_size: 30
        text: "{}.000".format(self.timer_duration)
        canvas:
            Color:
                rgb: 0,1,0
            Line:
                circle:self.center_x, self.center_y, 90, 0, self.angle % 360
                width: 30


<RootWidget>:
    #:import randint  random.randint
    orientation: "vertical"
    Timer:
        timer_duration: 10
    Timer:
        timer_duration: 20
        ''')

class CountDown(BoxLayout):
    timer_duration = NumericProperty(0)
    pass

class RootWidget(BoxLayout):
    pass


class SecondLabel(Label):
    pass


class CountDownLbl(Label):
    angle = NumericProperty(0)
    timer_duration = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CountDownLbl, self).__init__(**kwargs)
        self.anim_duration = self.timer_duration
        self.in_progress = False

    def start(self):
        print(self.ids)
        if not self.in_progress:
            self.anim_duration += self.timer_duration
            self.anim = Animation(angle=360 * self.anim_duration,  duration=self.timer_duration)
            self.in_progress = True
            self.anim.bind(on_complete=self.finish, on_progress=self.update_timer)
            self.anim.start(self)

    def finish(self, animation, widget):
        widget.text = "FINISHED"
        self.in_progress = False

    def update_timer(self, animation, widget, progression):
        text = ((self.timer_duration * 60000)*(1-progression))/60000
        widget.text = "{0:.3f}".format(float(text))


class TestApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    TestApp().run()
