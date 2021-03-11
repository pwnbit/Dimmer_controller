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


def set_time_sync(led):
    led.setClock()
    led.update_state()


def percent_to_byte(percent):
    percent = int(percent)
    if percent > 100:
        percent = 100
    if percent < 0:
        percent = 0
    return int(round(percent * 255/100, 0))


def byte_to_percent(byte):
    byte = int(byte)
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
    percent = byte_to_percent(led.brightness)
    led.update_state()
    return percent


def change_brightness(led, percent):
    byte = percent_to_byte(percent)
    led.setRgb(255, 0, 0, brightness=byte)
    led.update_state()


if __name__ == '__main__':
    VER = "v1.0.0"
    TITLE = "Dimmer Controller"

    bulb = None
    gui.set_options(font=('맑은 고딕', 9))
    gui.theme('Dark Grey 2')

    # section1 : 연결 전 보여질 부분
    section1 = [
        [gui.Text("Dimmer IP", size=(12, 1)), gui.Input("192.168.168.28", key='_IP', size=(14, 1)),
         gui.Button("Connect", key='_CONNECT', size=(9, 1), bind_return_key=True),
         gui.Button("Disconnect", key='_DISCONNECT', size=(9, 1), disabled=True, visible=False)],
        [gui.Text("Dimmer 시간", size=(12, 1)), gui.InputText("", key="_CLOCK", size=(19, 1), readonly=True), gui.Button("Sync", key='_SYNC', pad=(6, 1))],
        [gui.Text("Dimmer 밝기", size=(12, 1)),
         gui.Slider((1, 100), key='_SLIDER', default_value=0, orientation='h', size=(17, 20), enable_events=True, disable_number_display=True, disabled=True),
         gui.Text("0%", key="_BRIGHTNESS", size=(5, 1), pad=(6, 0))]
    ]

    # section2 : 연결 후 보여질 부분
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

    # Layout
    layout = [
        [gui.Text(f"{TITLE} - {VER}", font=('맑은 고딕', 18), text_color='#3399ff')],
        [gui.pin(gui.Column(section1, key='_SECTION1'))],
        [gui.pin(gui.Column(section2, key='_SECTION2', visible=False))],
        [gui.Text('Blog: https://blog.naver.com/ic21107', key='_BLOG', pad=(2, 1), enable_events=True)],
        [gui.Text('Github: https://github.com/pwnbit/Dimmer_controller', key='_GITHUB', pad=(2, 1), enable_events=True)]
    ]

    window = gui.Window(f"{TITLE} - {VER}", layout, finalize=True, icon="icon.ico")

    while True:
        event, values = window.read()

        if event == gui.WINDOW_CLOSED:
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
            window['_CONNECT'].update(disabled=True, visible=False)
            window['_DISCONNECT'].update(disabled=False, visible=True)
            window['_BRIGHTNESS'].update(f"{get_brightness(bulb)}%")
            window['_SLIDER'].update(get_brightness(bulb), disabled=False)
            # Update _SECTION2
            window['_CLOCK'].update(bulb.getClock())
            window['_TIMER'].update(bulb.getTimers())
            window['_SECTION2'].update(visible=True)
        elif event == '_DISCONNECT':
            # Update _SECTION1
            window['_IP'].update(disabled=False)
            window['_CONNECT'].update(disabled=False, visible=True)
            window['_DISCONNECT'].update(disabled=True, visible=False)
            window['_BRIGHTNESS'].update("0%")
            window['_SLIDER'].update("0", disabled=True)
            # Update _SECTION2
            window['_CLOCK'].update("")
            window['_SECTION2'].update(visible=False)
            window['_TIMER'].update(bulb.getTimers())
            if bulb:
                bulb.close()

        # Change Brightness
        elif event in ('_0', '_20', '_40', '_60', '_80', '_100'):
            change_brightness(bulb, event.replace("_", ""))
            window['_BRIGHTNESS'].update(f"{get_brightness(bulb)} %")
            window['_SLIDER'].update(get_brightness(bulb))
        elif event == '_APPLY':
            change_brightness(bulb, values['_MANUAL'])
            window['_BRIGHTNESS'].update(f"{get_brightness(bulb)} %")
            window['_SLIDER'].update(get_brightness(bulb))
        elif event == '_SLIDER':
            change_brightness(bulb, values['_SLIDER'])
            window['_BRIGHTNESS'].update(f"{get_brightness(bulb)} %")
            window['_SLIDER'].update(get_brightness(bulb))
        # Etc.
        elif event == '_SYNC':
            set_time_sync(bulb)
            window['_CLOCK'].update(bulb.getClock())
        elif event == '_BLOG':
            system('start "" https://blog.naver.com/ic21107')
        elif event == '_GITHUB':
            system('start "" https://github.com/pwnbit/Dimmer_controller')
    if bulb:
        bulb.close()
    window.close()
