import PySimpleGUI as gui
import socket
import flux_led
import re
from os import system
from time import sleep
import threading

# PySimpleGUI : https://pypi.org/project/PySimpleGUI/
# PySimpleGUI cookbook : https://pysimplegui.readthedocs.io/en/latest/cookbook/


def led_connect(ip):
    led = flux_led.WifiLedBulb(ipaddr=ip, timeout=1)
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


def verify_val(val_type, val):
    if val_type == 'ip':
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', val):
            return True
    elif val_type == 'number':
        if val.isnumeric():
            return True
    return False


def alert(message):
    gui.popup(message, title="Dimmer Controller", icon="icon.ico")


class scan_task:
    def __init__(self):
        self._running = True
        self.device_list = []

    def terminate(self):
        self._running = False

    def scanner(self, window):
        ip_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip_sock.connect(("pwnbit.kr", 443))
        subnet = '.'.join(ip_sock.getsockname()[0].split('.')[0:3])
        ip_sock.close()
        ip = 1
        while True:
            if self._running and ip < 256:
                lookup_ip = f"{subnet}.{ip}"
                find_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                find_sock.settimeout(0.1)
                try:
                    find_sock.sendto(b'HF-A11ASSISTHREAD', (lookup_ip, 48899))
                    data = find_sock.recvfrom(100)
                    if type(data[0]) is bytes and type(data[1] is tuple):
                        data_str = data[0].decode('ascii').split(',')
                        self.device_list.append(data_str[0])
                    find_sock.close()
                except socket.timeout:
                    pass
                except ConnectionResetError:
                    pass
                ip += 1
                window.write_event_value('_SCANPROGRESS', (ip, self.device_list))
            else:
                break


def scan():
    thread = scan_task()
    t = threading.Thread(target=thread.scanner, args=(window, ), daemon=True).start()
    return thread


def scan_cancel(c):
    c.terminate()


if __name__ == '__main__':
    VER = "v1.3.1"
    TITLE = "Dimmer Controller"

    bulb = None
    gui.set_options(font=('맑은 고딕', 9))
    gui.theme('Dark Grey 2')

    # section1 : 연결 전 보여질 부분
    section1 = [
        [gui.Text("Dimmer IP", size=(12, 1)), gui.Input("", key='_IP', size=(14, 1)),
         gui.Button("Connect", key='_CONNECT', size=(9, 1), bind_return_key=True),
         gui.Button("Disconnect", key='_DISCONNECT', size=(9, 1), disabled=True, visible=False)],
        [gui.Text("Dimmer 시간", size=(12, 1)), gui.InputText("", key="_CLOCK", size=(19, 1), readonly=True), gui.Button("Sync", key='_SYNC', pad=(6, 1))],
        [gui.Text("Dimmer 밝기", size=(12, 1)),
         gui.Slider((1, 100), key='_SLIDER', default_value=0, orientation='h', size=(17, 20), enable_events=True, disable_number_display=True, disabled=True),
         gui.Text("0%", key="_BRIGHTNESS", size=(5, 1), pad=(6, 0))]
    ]

    # section2 : 연결 후 보여질 부분
    section2 = [
        [gui.HSeparator()],
        [gui.Frame("Presets", [
            [gui.Button("0%", key='_0', disabled=True), gui.Button("20%", key='_20', disabled=True), gui.Button("40%", key='_40', disabled=True),
             gui.Button("60%", key='_60', disabled=True), gui.Button("80%", key='_80', disabled=True), gui.Button("100%", key='_100', disabled=True),
             gui.Text("│", pad=(0, 0)),
             gui.InputText("", key='_MANUAL', size=(3, 1), disabled=True), gui.Text("%", pad=(0, 0)), gui.Button("Apply", key='_APPLY', disabled=True)]
        ])],
        [gui.Frame("Timer Settings", [[
            gui.Listbox(values=('Unset', 'Unset', 'Unset', 'Unset', 'Unset', 'Unset'), key='_TIMER', size=(70, 6), no_scrollbar=True)]])]
    ]

    # Layout
    layout = [
        [
            gui.Column([[gui.Button("Scan", key="_SCAN", size=(8, 1)),
                         gui.Text("0%", size=(4, 1), key='_PG')],
                        [gui.Listbox(values=(), key='_DEVICE', size=(14, 18), no_scrollbar=True, enable_events=True)]
                        ]),
            gui.Column([[gui.Text(f"{TITLE} - {VER}", font=('맑은 고딕', 18), text_color='#3399ff')],
                        [gui.pin(gui.Column(section1, key='_SECTION1'))],
                        [gui.pin(gui.Column(section2, key='_SECTION2'))],
                        [gui.Text('Blog: https://blog.naver.com/ic21107', key='_BLOG', pad=(2, 1), enable_events=True)],
                        [gui.Text('Github: https://github.com/pwnbit/Dimmer_controller', key='_GITHUB', pad=(2, 1), enable_events=True)]
                        ])
        ]
    ]

    window = gui.Window(f"{TITLE} - {VER}", layout, finalize=True, icon="icon.ico")
    window_active = False
    thread = ""
    flag_scan = True
    while True:
        event, values = window.read()
        print(event, values)

        if event == gui.WINDOW_CLOSED:
            if bulb:
                bulb.close()
            window.close()
            break
        elif event == '_CONNECT':
            try:
                if not verify_val('ip', values['_IP']):
                    alert("입력한 IP를 확인 해주세요.")
                else:
                    bulb = led_connect(values['_IP'])
                    bulb.update_state()
                    # Update _SECTION1
                    window['_IP'].update(disabled=True)
                    window['_CONNECT'].update(disabled=True, visible=False)
                    window['_DISCONNECT'].update(disabled=False, visible=True)
                    window['_BRIGHTNESS'].update(f"{get_brightness(bulb)}%")
                    window['_SLIDER'].update(get_brightness(bulb), disabled=False)
                    # Update _SECTION2
                    window['_CLOCK'].update(bulb.getClock())
                    window['_TIMER'].update(bulb.getTimers())
                    window['_0'].update(disabled=False)
                    window['_20'].update(disabled=False)
                    window['_40'].update(disabled=False)
                    window['_60'].update(disabled=False)
                    window['_80'].update(disabled=False)
                    window['_100'].update(disabled=False)
                    window['_MANUAL'].update(disabled=False)
                    window['_APPLY'].update(disabled=False)
            except socket.timeout:
                alert("연결 시간이 초과 되었습니다. 장치의 연결 상태를 확인 해주세요.")

        elif event == '_DISCONNECT':
            # Update _SECTION1
            window['_IP'].update("", disabled=False)
            window['_CONNECT'].update(disabled=False, visible=True)
            window['_DISCONNECT'].update(disabled=True, visible=False)
            window['_BRIGHTNESS'].update("0%")
            window['_SLIDER'].update("0", disabled=True)
            # Update _SECTION2
            window['_CLOCK'].update("")
            window['_TIMER'].update(bulb.getTimers())
            window['_0'].update(disabled=True)
            window['_20'].update(disabled=True)
            window['_40'].update(disabled=True)
            window['_60'].update(disabled=True)
            window['_80'].update(disabled=True)
            window['_100'].update(disabled=True)
            window['_MANUAL'].update(disabled=True)
            window['_APPLY'].update(disabled=True)
            if bulb:
                bulb.close()

        # Change Brightness
        elif event in ('_0', '_20', '_40', '_60', '_80', '_100'):
            change_brightness(bulb, event.replace("_", ""))
            window['_BRIGHTNESS'].update(f"{get_brightness(bulb)} %")
            window['_SLIDER'].update(get_brightness(bulb))
        elif event == '_APPLY':
            if not verify_val('number', values['_MANUAL']):
                alert("숫자만 입력 해주세요.")
            else:
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
        elif event == '_SCAN' and flag_scan:
            window['_SCAN'].update("Cancel")
            flag_scan = False
            thread = scan()
        elif event == '_SCANPROGRESS':
            window['_PG'].update(f"{int(values['_SCANPROGRESS'][0] / 255 * 100)}%")
            if values['_SCANPROGRESS'][1]:
                window['_DEVICE'].update(values['_SCANPROGRESS'][1])
        elif event == '_SCAN' and not flag_scan:
            flag_scan = True
            scan_cancel(thread)
            window['_SCAN'].update("Scan")
        elif event == '_DEVICE':
            if values['_DEVICE']:
                window['_IP'].update(values['_DEVICE'][0])

