# poxy
a useful tool to get proxy to the website which you can't reach at present.

only support windows with IPV4 at present.

now it support zh_CN and en_US locale.

NOTE: before using it, you have to get the r/w permission of hosts file.

usage:

search proxy for unreachable foreign websites .

Options:

Usage: poxy.py [OPTIONS]

search proxy for unreachable foreign websites .

Options:

-h --help               Display usage information and exit.

-v --verbose            Display detail information.

-t msec --timeout=msec  Set timeout time for connection tries.default is 1000ms

-d url --target=url     Set target url.

-f --force              force to overwrite hosts file if target is in it.

--model=X                 choose an model: proxy or alternate

--modellevel=X            set model level: 1 or greater.

example:

poxy -f -v -t 1000 --model=proxy --modellevel=1 -d https://www.google.com.hk/?gws_rd=ssl

poxy -f -v -t 1000 --model=alternate --modellevel=1 -d https://www.google.com.hk/?gws_rd=ssl
