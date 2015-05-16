import logging
import http.client
import urllib.parse

__author__ = 'yufeng'
# use it to get specific web as it has special 
# requirement.


logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s  %(message)s')
logger.BASIC = logging.WARN
logger.DETAIL = logging.INFO

DEFAULT_TIMEOUT = 3000


class WebClient():
    def __init__(self):
        self.client = None
        self.target = None

    def set_target(self, host, port=80, timeout=DEFAULT_TIMEOUT):
        self.client = http.client.HTTPConnection(host, port, timeout)
        self.target = host

    def put_def_header(self):
        self.client.putheader('User-Agent',
                              'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0')
        self.client.putheader('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        self.client.putheader('Accept-Language', 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3')
        self.client.putheader('Accept-Encoding', 'text, deflate')
        self.client.putheader('Connection', 'keep-alive')
        self.client.putheader('Referer', 'http://{0}/'.format(self.target))
        self.client.putheader('Content-Type', 'application/x-www-form-urlencoded')
        self.client.putheader('DNT', '1')

    def putheader(self, header, value):
        assert isinstance(header, str)
        assert isinstance(value, str)
        self.client.putheader(header, value)

    def start_request(self, method="POST", url="/", data=None):
        """
        :param method:
        :param url:
        :param data: data to send to server.
        :return: str
        """
        raw_data = None
        try:
            self.client.connect()
            if method == "GET":
                self.client.putrequest(method, url + data)
                data = ""
            else:
                self.client.putrequest(method, url)
            data = urllib.parse.quote(data, '=&')
            self.client.putheader('Content-Length', len(data))
            self.put_def_header()
            self.client.endheaders()
            self.client.send(data.encode())
            anwser = self.client.getresponse()
            if anwser.status != 200:
                logger.warning("failed to get response from server! error: {0}".format(anwser.status))
            raw_data = str(anwser.read().decode())
        except Exception as err:
            logger.log(logging.ERROR, err)  # when error happened, it often means there is still a connection
            # thus just ignore it.
        self.client.close()
        return raw_data