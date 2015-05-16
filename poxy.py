import argparse
import sys
import io

from module import proxy


__author__ = 'yufeng'


class Poxy():
    def __init__(self):
        self.__proxy = proxy.Proxy()
        self.__setting = "proxy.settings"

    def set_outfile(self, _file):
        if isinstance(_file, str):
            fp = open(_file, mode='w')
            self.__proxy.out = fp
        elif isinstance(_file, io.TextIOWrapper):
            self.__proxy.out = _file

    def set_format(self, _format):
        self.__proxy.format = _format

    def set_target(self, target):
        self.__proxy.target = target

    def set_check(self, check):
        self.__proxy.check = check

    def set_setting(self, setting):
        self.__setting = setting

    def set_interval(self, interval):
        self.__proxy.interval = interval

    def run(self):
        self.__proxy.read_setting(self.__setting)
        self.__proxy.extract()

    def init(self):
        arg_parser = argparse.ArgumentParser(description="a tool to crawl proxies from web.",
                                             epilog="for more detail information,please read help.html.")
        arg_parser.add_argument("-o", "--out", nargs="?", default=sys.stdout,
                                help="the file writen proxies to. default: stdout")
        arg_parser.add_argument("-f", "--format", nargs="?", default="{0}:{1}\n",
                                help="the proxy output format. default: \"{0}:{1}\\n\". read" +
                                     " help.html for more information.")
        arg_parser.add_argument("--check", action="store_const", const=True, default=False,
                                help="check the proxy validation.")
        arg_parser.add_argument("--target", nargs="?", default="https://github.com",
                                help="a url for checking proxy validation. default:https://github.com")
        arg_parser.add_argument("--config", nargs="?", default="proxy.settings",
                                help="the proxy setting file. default: proxy.settings")
        arg_parser.add_argument("--interval", nargs="?", type=int, default=1,
                                help="the interval between two requests. some sever has strict limitation at it.")
        arg = arg_parser.parse_args()
        self.set_target(arg.target)
        self.set_check(arg.check)
        self.set_format(arg.format)
        self.set_outfile(arg.out)
        self.set_setting(arg.config)
        self.set_interval(arg.interval)
        self.run()


if __name__ == "__main__":
    poxy = Poxy()
    poxy.init()