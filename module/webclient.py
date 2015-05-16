import http.client
import urllib.parse

from module.errsys import logger


__author__ = 'yufeng'
# use it to get specific web as it has special 
# requirement.

DEFAULT_TIMEOUT = 3000


class WebClient():
    def __init__(self):
        self.__client = None
        self.__target = None
        self.__client_header = {}

    def set_target(self, host, port=80, timeout=DEFAULT_TIMEOUT):
        self.__target = urllib.parse.urlparse(host)
        if self.__target.netloc == '' or self.__target.scheme == '':
            self.__target = urllib.parse.urlparse("http://" + host)
        self.__client = http.client.HTTPConnection(self.__target.netloc, port, timeout)

    def set_proxy(self, host, port=80):
        self.__client.set_tunnel(host, port)

    def __put_def_header(self):
        pass
        self.__client.putheader("User-Agent", "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:38.0)")
        self.__client.putheader('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        self.__client.putheader('Accept-Language', 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
        self.__client.putheader('Accept-Encoding', 'text, deflate')
        self.__client.putheader('Connection', 'keep-alive')
        self.__client.putheader('Referer', 'http://{0}/'.format(self.__target.netloc))
        self.__client.putheader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
        self.__client.putheader('DNT', '1')

    def __put_client_header(self):
        for header, value in self.__client_header.items():
            self.__client.putheader(header, value)

    def putheader(self, header, value):
        assert isinstance(header, str)
        assert isinstance(value, str)
        self.__client_header[header] = value

    def start_request(self, method="GET", url="", data=""):
        """
        :param method:
        :param url:
        :param data: data to send to server.
        :return: str
        """
        url = self.__target.path + url
        raw_data = None
        try:
            self.__client.connect()
            if method == "GET":
                data = url + data
                data = str.replace(data, r'//', r'/')
                self.__client.putrequest(method, data)
                data = ""
            else:
                self.__client.putrequest(method, url)
            data = urllib.parse.quote(data, '=&')
            self.__client.putheader('Content-Length', len(data))
            self.__put_def_header()
            self.__put_client_header()
            self.__client.endheaders()
            self.__client.send(data.encode())
            anwser = self.__client.getresponse()
            if anwser.status != 200:
                logger.warning(
                    "failed to get response from server! error: {0}".format(http.client.responses[anwser.status]))
            raw_data = str(anwser.read().decode())
        except Exception as err:
            logger.log(logger.DETAIL, str(err) + " when request to {0}".format(
                self.__target.netloc + self.__target.path))  # when error happened, it often
            # means there is still a connection
            # thus just ignore it.
        self.__client.close()
        return raw_data


