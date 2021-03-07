import PySimpleGUI as gui
import socket
import flux_led
from os import system
from time import sleep

# PySimpleGUI : https://pypi.org/project/PySimpleGUI/
# PySimpleGUI cookbook : https://pysimplegui.readthedocs.io/en/latest/cookbook/


def led_connect(ip):
    led = flux_led.WifiLedBulb(ipaddr=ip, timeout=3)
    led.update_state()
    return led


def get_status(led):
    led.update_state()
    return led


def percent_to_byte(percent):
    if percent > 100:
        percent = 100
    if percent < 0:
        percent = 0
    return int(round(percent * 255/100, 0))


def byte_to_percent(byte):
    if byte > 255:
        byte = 255
    if byte < 0:
        byte = 0
    return int(round(byte * 100/255, 0))


def sunrise_mode(led):
    for i in range(0, 100, 5):
        i = percent_to_byte(i)
        led.setRgb(255, 0, 0, brightness=i)
        sleep(0.1)


def sunset_mode(led):
    for i in range(100, 0, -5):
        i = percent_to_byte(i)
        led.setRgb(0, 0, 0, brightness=i)
        sleep(0.1)


def get_brightness(led):
    b = byte_to_percent(led.brightness)
    led.update_state()
    return b


def change_brightness(led, percent):
    byte = percent_to_byte(percent)
    led.setRgb(255, 0, 0, brightness=byte)
    led.update_state()


if __name__ == '__main__':
    VER = "v0.1.1"
    TITLE = "Dimmer Controller"

    bulb = None
    gui.set_options(font=('맑은 고딕', 9))
    gui.theme('Dark Grey 2')

    section1 = [
        [gui.Text("Dimmer IP", size=(12, 1)), gui.Input("", key='_IP', size=(15, 1)), gui.Button("Connect", key='_CONNECT', bind_return_key=True)],
        [gui.Text("Dimmer 시간", size=(12, 1)), gui.InputText("", key="_CLOCK", size=(24, 1), readonly=True)],
        [gui.Text("Dimmer 밝기", size=(12, 1)),
         gui.Slider((1, 100), key='_SLIDER', default_value=0, orientation='h', size=(16, 20), enable_events=True, disable_number_display=True, disabled=True),
         gui.Text("0%", key="_BRIGHTNESS", size=(5, 1), pad=(0, 0))]
    ]
    section2 = [
        [gui.Text("─" * 23)],
        [gui.Frame("Presets", [
            [gui.Button("0%", key='_0'), gui.Button("20%", key='_20'), gui.Button("40%", key='_40'),
             gui.Button("60%", key='_60'), gui.Button("80%", key='_80'), gui.Button("100%", key='_100'), gui.Text("│", pad=(0, 0)),
             gui.InputText("", key='_MANUAL', size=(3, 1)), gui.Text("%", pad=(0, 0)), gui.Button("Apply", key='_APPLY')],
        ])],
        [gui.Frame("Timer Settings", [[
            gui.Listbox(values=(), key="_TIMER", size=(0, 6), no_scrollbar=True, auto_size_text=True, select_mode=gui.SELECT_MODE_SINGLE)]])]
    ]

    layout = [
        [gui.Text(f"{TITLE} - {VER}", font=('맑은 고딕', 18), text_color='#3399ff')],
        [gui.pin(gui.Column(section1, key='_SECTION1', visible=False))],
        [gui.pin(gui.Column(section2, key='_SECTION2', visible=False))],
        [gui.Text('Blog: https://blog.naver.com/ic21107', key='_BLOG', enable_events=True)],
        [gui.Text('Github: https://github.com/pwnbit/Dimmer_controller', key='_GITHUB', enable_events=True)]
    ]

    window = gui.Window(f"{TITLE} - {VER}", layout, finalize=True)
    window['_SECTION1'].update(visible=True)

    while True:
        event, values = window.read()
        # print(f'{event}, {values}')

        if event == gui.WINDOW_CLOSED or event == 'Quit':
            break
        elif event == '_CONNECT':
            try:
                bulb = led_connect(values['_IP'])
                bulb.update_state()
            except socket.timeout:
                print("timeout")
                exit(1)
            # Update _SECTION1
            window['_IP'].update(disabled=True)
            window['_CONNECT'].update(disabled=True)
            window['_BRIGHTNESS'].update(f"{get_brightness(bulb)} %")
            window['_SLIDER'].update(value=get_brightness(bulb))
            # Update _SECTION2
            window['_CLOCK'].update(bulb.getClock())
            window['_TIMER'].update(bulb.getTimers())
            window['_SLIDER'].update(disabled=False)
            window['_SECTION2'].update(visible=True)
            print(get_status(bulb))

        # Change Brightness
        elif event in ('_0', '_20', '_40', '_60', '_80', '_100'):
            change_brightness(bulb, event.replace("_", ""))
            window['_BRIGHTNESS'].update(f"{get_brightness(bulb)} %")
            window['_SLIDER'].update(value=get_brightness(bulb))
        elif event == '_APPLY':
            change_brightness(bulb, values['_MANUAL'])
            window['_BRIGHTNESS'].update(f"{get_brightness(bulb)} %")
            window['_SLIDER'].update(value=get_brightness(bulb))
        elif event == '_SLIDER':
            change_brightness(bulb, values['_SLIDER'])
            window['_BRIGHTNESS'].update(f"{get_brightness(bulb)} %")
            window['_SLIDER'].update(value=get_brightness(bulb))
        elif event == '_BLOG':
            system('start "" https://blog.naver.com/ic21107')
        elif event == '_GITHUB':
            system('start "" https://github.com/pwnbit/Dimmer_controller')

    if bulb:
        bulb.close()
    window.close()
