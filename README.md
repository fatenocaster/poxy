usage: poxy.py [-h] [-o [OUT]] [-f [FORMAT]] [--check] [--target [TARGET]]
               [--config [CONFIG]] [--interval [INTERVAL]]

a tool to crawl proxies from web.

optional arguments:

  -h, --help            show this help message and exit
  
  -o [OUT], --out [OUT]
  
                        the file writen proxies to. default: stdout
                        
  -f [FORMAT], --format [FORMAT]
  
                        the proxy output format. default: "{0}:{1}\n". read
                        
                        help.html for more information.
                        
  --check               check the proxy validation.
  
  --target [TARGET]     a url for checking proxy validation.
  
                        default:https://github.com
                        
  --config [CONFIG]     the proxy setting file. default: proxy.settings
  
  --interval [INTERVAL]
  
                        the interval between two requests. some sever has
                        
                        strict limitation at it.

for more detail information,please read doc files.
