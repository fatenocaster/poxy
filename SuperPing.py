import argparse
import time
import sys

__author__ = 'yufeng'
from module.errsys import logger
import re
import http.client
# it's to help find alternative ips for
# specific website.
from module import webclient
from htmldom import htmldom


class Loaner:
    def __init__(self):
        self.timeout = webclient.DEFAULT_TIMEOUT  # should not be short like 100 otherwise it may fail to connect.
        self.port = 80
        self._host = [("ping.chinaz.com", ["host={0}&checktype=0&linetype=海外", "POST"]),
                      ("www.super-ping.com", ["?ping={0}&locale=en", "GET"])]  # the tool website
        self.chinaz = 0
        self.super_ping = 1
        self._key_data_pattern = {self.chinaz: ["var[\s]*json=({.*})", "var[\s]enkey=\'(.*)\'", "guid:([\d\w\-]*)"],
                                  self.super_ping: ["load\(\'\.([^\']+)"]}
        self._parser = {self.chinaz: self.parse_chinaz_list, self.super_ping: self.parse_superping_list}
        self._test_conf = {self.chinaz: ["POST", "/iframe.ashx?t=ping&callback="], self.super_ping: ["GET", "/"]}
        self.key_list = []
        self.target = None
        self.result_pattern = [{"ip": "result:\{ip:\'([\d\.]+)\'", "ipaddress": "ipaddress:\'([^,]+)\'",
                                "responsetime": "responsetime:\'([\d]+)[^,]*\'"},
                               {"ip": "ping-ip\'>([\d\.]+)", "ipaddress": "node=([^\']+)",
                                "responsetime": "ping-avg\'>([\d\.]+)"}]  # to get response message.
        self.candidates = []

    def found_key_data(self, data, host_index):
        result = False
        try:
            for k_pattern in self._key_data_pattern[host_index]:
                if re.search(k_pattern, data):
                    result = True
        except ValueError:
            pass
        except AttributeError:
            pass
        return result

    def hunt(self, host_index):
        """
        host_index must be self.super_ping or self.chinaz.
        :param host_index:
        :return:a list with checked ips.
        """
        wc = webclient.WebClient()
        host_url, key = self._host[host_index]
        wc.set_target(host_url, timeout=self.timeout)
        result = wc.start_request(key[1], data=key[0].format(self.target))
        try:
            dom = htmldom.HtmlDom().createDom(result)
            for item in dom.find("script"):
                if self.found_key_data(item.text(), host_index):
                    self._parser[host_index](item.text())
        except Exception as err:
            logger.log(logger.BASIC, err)
        self.get_candidate(host_index)
        self.check()
        return self.candidates

    def parse_chinaz_list(self, key_data):
        try:
            pattern = self._key_data_pattern[self.chinaz]
            sm = re.search(pattern[0], key_data)
            enkey = re.search(pattern[1], key_data)
            enkey = enkey.group(1)
            mdata = str(sm.group(1).replace('\'', ''))
            while re.search(pattern[2], mdata):
                sm = re.search(pattern[2], mdata)
                self.key_list.append(
                    "guid={0}&host={1}&ishost=false&encode={2}&checktype=0".format(sm.group(1), self.target, enkey))
                mdata = mdata[sm.end(1):]
        except ValueError:
            pass
        except AttributeError:
            pass

    def parse_superping_list(self, key_data):
        try:
            pattern = self._key_data_pattern[self.super_ping]
            while re.search(pattern[0], key_data):
                sm = re.search(pattern[0], key_data)
                key_data = key_data[sm.end(1):]
                self.key_list.append(sm.group(1))
        except ValueError:
            pass
        except AttributeError:
            pass

    def parse_response(self, server_msg, host_index):
        msg = {}
        for (key, sm) in self.result_pattern[host_index].items():
            result = re.search(sm, server_msg)
            if result:
                msg[key] = str(result.group(1))
        if msg.get("responsetime", None) is None:
            msg = {}
        else:
            msg.pop("responsetime")
        return msg

    def check(self):
        tmp = []
        try:
            for item in self.candidates:
                timeout = self.get_delay_time(item["ip"])
                if timeout:
                    item["responsetime"] = float(timeout)
                    tmp.append(item)
                    logger.log(logger.DETAIL,
                               "got a candidate ip:{0} delay:{1}s".format(item["ip"], item["responsetime"]))
        except Exception as err:
            logger.log(logger.BASIC, err)
        self.candidates = tmp

    def get_delay_time(self, _host):
        chk = http.client.HTTPConnection(_host, self.port, self.timeout)
        rtn = None
        try:
            tick = time.perf_counter()
            chk.connect()
            chk.request("GET", "/")
            chk.getresponse().read()
            chk.close()
            rtn = time.perf_counter() - tick
        except TimeoutError:
            pass
        chk.close()
        return rtn

    def get_candidate(self, host_index):
        wc = webclient.WebClient()
        test_conf = self._test_conf[host_index]
        host_url, key = self._host[host_index]
        wc.set_target(host_url, timeout=self.timeout)
        for item in self.key_list:
            response = wc.start_request(test_conf[0], test_conf[1], item)
            if response:
                result = self.parse_response(response, host_index)
                if result != {}:
                    if result not in self.candidates:
                        self.candidates.append(result)
                        logger.log(logger.DETAIL,
                                   "got an alpha ip:{0}".format(result["ip"]))


def super_ping():
    arg_parser = argparse.ArgumentParser(description="a tool to make super ping.")
    arg_parser.add_argument("--chanel", nargs="?", type=int, choices=[1, 2], default=1,
                            help="choose the ping chanel.")
    arg_parser.add_argument("--target", nargs="?", required=True,
                            help="set the target to ping.")
    arg = arg_parser.parse_args()
    ping = Loaner()
    ping.target = arg.target
    if arg.chanel == 1:
        ping.hunt(ping.chinaz)
    elif arg.chanel == 2:
        ping.hunt(ping.super_ping)


if __name__ == "__main__":
    super_ping()