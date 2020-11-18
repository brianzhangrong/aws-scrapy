import json
import random
# import redis
import time
# import requests


class ProxyMiddleware(object):
    def __init__(self):
        with open('proxy.json', 'r') as f:
            self.proxies = json.load(f)
            # self.r = redis.Redis(host="redis-01.db.sit.ihomefnt.org", port=6379, password="aijia1234567",db=6)

    def process_request(self, request, spider):
        while True:
            proxy = random.choice(self.proxies)
            if self.proxyReady(proxy):
                request.meta['proxy'] = 'http://{}:57114'.format(proxy)
                print('---------','http://{}:57114'.format(proxy))
                break

    def proxyReady(self, proxy):
        return True
        # key = proxy + "aws"
        # retult = self.r.exists(key)
        # if retult:
        #     return False
        # else:
        #     self.r.setex(key, 1, 15)
        #     return True
