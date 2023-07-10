#!/usr/bin/env python3

import signal
from time import sleep
from urllib3 import disable_warnings as disable_urllib_warnings
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from subprocess import TimeoutExpired

from pyzabbix import ZabbixAPI

API_URL = 'https://YOUR-ZABBIX.DOMAIN/zabbix'
API_USER = 'YOUR-ZABBIX-API-USER'
API_PWD = 'YOUR-ZABBIX-API-PWD'

AMPEL_CMD = '/usr/local/sbin/USBswitchCmd'
CHECK_INTERVAL = 10
DEBUG = False
TIMEOUT = 10  # to fix the stuck-blinking
CHOICES = {2: 'g', 3: 'y', 4: 'r', 5: '-i 100', None: 'o'}  # max-priority to cmd-action mapping


class Ampel:
    def __init__(self):
        self.PRIORITY = None  # to save the current state
        self.ZABBIX_SESSION = None
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def run(self):
        self.start_session()

        try:
            self.set_color(None)

            while True:
                self.get_problems()
                sleep(CHECK_INTERVAL)

        except (Exception, KeyboardInterrupt) as error:
            self.exit(error=error)

    def exit(self, signum=None, stack=None, error=None):
        if error is not None:
            print(f'An unexpected error occurred: {error}')

        elif signum is not None:
            print(f'Got signal {signum}')

        self.set_color(None)
        raise SystemExit()

    def _process(self, command):
        try:
            subprocess_popen([command], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate(timeout=TIMEOUT)

        except TimeoutExpired:
            self.exit()  # exit to reset blinking

    def start_session(self):
        disable_urllib_warnings()

        self.ZABBIX_SESSION = ZabbixAPI(API_URL)
        self.ZABBIX_SESSION.session.verify = False
        self.ZABBIX_SESSION.login(API_USER, API_PWD)

        if DEBUG:
            print('Connected to Zabbix API Version {zapi.api_version()}')

    def set_color(self, new_priority: (None, str)):
        if new_priority is not None and new_priority != self.PRIORITY:
            # reset color
            print(f'Priority changed from {self.PRIORITY} to {new_priority}')
            self.set_color(None)

        self.PRIORITY = new_priority
        self._process(f'{AMPEL_CMD} {CHOICES[new_priority]}')

    def get_problems(self):
        result = self.ZABBIX_SESSION.trigger.get(
            filter=1,
            monitored=1,
            only_true=1,
            sortfield='priority',
            sortorder='DESC',
            output=['triggerid', 'priority', 'value', 'acknowledged'],
            withLastEventUnacknowledged=1,
            maintenance=False,
        )

        state_list = [state for state in result if int(state['value']) == 1]
        current_alert_list = []

        for _ in state_list:
            current_alert_list.append(int(_['priority']))

        self.set_color(new_priority=max(current_alert_list))  # send highest current priority to color-picker


if __name__ == '__main__':
    Ampel().run()
