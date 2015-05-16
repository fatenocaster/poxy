import re
import itertools
import sys
import urllib.parse
import urllib.request
import threading

import SettingReader
from errsys import logger
from htmldom import htmldom
import webclient


__author__ = 'yufeng'


def get_scheme(url):
    url_type = urllib.parse.urlparse(url)
    if url_type.scheme:
        return url_type.scheme
    else:
        return "http"


def is_validate(proxy_ip, proxy_port, target, check):
    result = False
    if check:
        rq = urllib.request.Request(target)
        rq.set_proxy(proxy_ip + ":" + proxy_port, get_scheme(target))
        try:
            response = urllib.request.urlopen(rq, timeout=5)
            response.read()
            result = True
        except Exception:
            pass
    else:
        result = True
    return result


class Proxy():
    def __init__(self):
        self.__setting = {}
        self.__web = webclient.WebClient()
        self.__proxies = []
        self.out = sys.stdout
        self.format = "{0}:{1}\n"
        self.check = False
        self.target = "https://github.com"
        self.__tasks = []

    def get_proxies(self):
        return self.__proxies

    def read_setting(self, setting):
        """
        :param setting: the setting file path.
        :return: final proxy collection setting.
        """
        setting_reader = SettingReader.ProxySettingReader()
        self.__setting = setting_reader.read(setting)
        return self.__setting

    def _find_proxy(self, ip_table, pattern):
        """
        :param ip_table: list of proxy with junk data.
        :param pattern: to search ip and port.
        :return:
        """
        valid_pattern = False
        for ip_item in ip_table:
            try:
                ip_item = ip_item.html().replace("\n", "").replace("\r", "").replace("\s", "")
                while re.search(pattern, ip_item):
                    valid_pattern = True
                    ip_port_sm = re.search(pattern, ip_item)
                    if is_validate(*ip_port_sm.groups(), target=self.target, check=self.check):
                        if ip_port_sm.groups() not in self.__proxies:
                            self.__proxies.append(ip_port_sm.groups())
                            print(self.format.format(*ip_port_sm.groups()), end="", file=self.out)
                    ip_item = ip_item[ip_port_sm.end(2):]
            except Exception as err:
                logger.log(logger.BASIC, str(err))
        if valid_pattern is False:
            raise SettingReader.ProxySettingError("invalid pattern!", pattern)

    def extract(self):
        for setting_name, setting in self.__setting.items():
            for base_url, selector, pattern in itertools.zip_longest(setting["base_url"], setting["selector"],
                                                                     setting["pattern"]):
                if base_url:
                    if pattern is None:
                        pattern = setting["pattern"][len(setting["pattern"]) - 1]
                    if selector is None:
                        selector = setting["selector"][len(setting["selector"]) - 1]
                    self.__web.set_target(base_url)
                    try:
                        html = self.__web.start_request()
                        dom = htmldom.HtmlDom().createDom(html)
                        table = dom.find(selector)
                        if table.len == 0:
                            raise SettingReader.ProxySettingError("invalid selector!", selector)
                        # td = threading.Thread(target=self._find_proxy, args=(table, pattern))
                        # td.start()
                        # self.__tasks.append(td)
                        self._find_proxy(table, pattern)
                    except Exception as err:
                        logger.log(logger.BASIC, str(err))
        for task in self.__tasks:
            task.join()