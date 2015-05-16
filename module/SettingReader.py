import urllib.parse
import time

__author__ = 'yufeng'
import json
import io
import re
import itertools

import jsmin

from module.errsys import logger
from htmldom import htmldom
from module import webclient


def absolute_url(base_url, relative_url):
    base = urllib.parse.urlparse(base_url)
    if base.scheme == "":
        base = urllib.parse.urlparse("http://"+base_url)
    relative = urllib.parse.urlparse(relative_url)
    if relative.netloc == '' or relative.scheme == '':
        return base.netloc+relative.path
    else:
        return relative_url


class SettingReader:
    def __init__(self):
        self.__setting = {}
        self.interval = 1

    def set_interval(self, interval):
        self.interval = interval

    def read(self, fp):
        if isinstance(fp, str):
            with open(fp) as jfile:
                mini_jfile = jsmin.jsmin(jfile.read())
                self.__setting = json.loads(mini_jfile)
        elif issubclass(fp, io.IOBase):
            mini_jfile = jsmin.jsmin(fp.read())
            self.__setting = json.loads(mini_jfile)
        else:
            self.__setting = {}
        return self.__setting


class ProxySettingReader(SettingReader):
    def __init__(self):
        super().__init__()
        self.__proxy_setting = {}
        self.__web = webclient.WebClient()

    def read(self, fp):
        self.__proxy_setting = super().read(fp)
        for setting in self.__proxy_setting.keys():
            self.__proxy_setting[setting]["base_url"] = self.__extract_baseurl(
                self.__proxy_setting[setting]["base_url"])
        return self.__proxy_setting

    def __extract_baseurl(self, base_url):
        if isinstance(base_url, list):
            return self.__extract_baseurl_mode1(base_url)
        elif isinstance(base_url, dict) and isinstance(base_url["base_url"], list):
            return self.__extract_baseurl_mode2(base_url)
        elif isinstance(base_url, dict) and isinstance(base_url["base_url"], dict):
            base_url["base_url"] = self.__extract_baseurl(base_url["base_url"])
            return self.__extract_baseurl(base_url)

    def __extract_baseurl_mode1(self, base_url):
        assert isinstance(base_url, list)
        return base_url

    def __extract_baseurl_mode2(self, base_url):
        """
        :return extracted base urls list.
        """
        urls = []
        for item_url, selector, pattern, attr in itertools.zip_longest(base_url["base_url"],
                                                                       base_url["selector"],
                                                                       base_url["pattern"],
                                                                       base_url["container_attr"]):
            if item_url:
                if pattern is None:
                    pattern = base_url["pattern"][len(base_url["pattern"])-1]
                if selector is None:
                    selector = base_url["selector"][len(base_url["selector"])-1]
                if attr is None:
                    attr = base_url["container_attr"][len(base_url["container_attr"])-1]
                time.sleep(self.interval)
                self.__web.set_target(item_url)
                try:
                    html = self.__web.start_request()
                    dom = htmldom.HtmlDom().createDom(html)
                    table = dom.find(selector)
                    for i in base_url["sequence"]:
                        if attr:
                            urls.append(absolute_url(item_url, table[int(i)].attr(attr)))
                        else:
                            url_sm = re.search(pattern, table[int(i)].html())
                            urls.append(absolute_url(item_url, url_sm.group(1)))
                except Exception as err:
                    logger.log(logger.BASIC, str(err))
        return urls


class SettingError(Exception):
    pass


class ProxySettingError(SettingError):
    """
    it raised when an setting is not correct.
    """

    def __init__(self, err_reason, err_setting, return_code=1):
        self.__err_setting = err_setting
        self.__return_code = return_code
        self.__err_reason = err_reason

    def __str__(self):
        return "error occurred at \nsetting:\"{0}\"\nreason: {1}".format(self.__err_setting, self.__err_reason)