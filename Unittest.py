import module.webclient
import time
__author__ = 'yufeng'
#
# proxy = Proxy()
# print(proxy.read_setting("proxy.settings"))
# proxy.extract()

wc = module.webclient.WebClient()
wc.set_target("www.haodailiip.com/guonei")
print(wc.start_request())
time.sleep(1)
wc.set_target("www.haodailiip.com/guonei/1")
print(wc.start_request())
time.sleep(1)
wc.set_target("www.haodailiip.com/guonei/2")
print(wc.start_request())
time.sleep(1)
wc.set_target("www.haodailiip.com/guonei/3")
print(wc.start_request())