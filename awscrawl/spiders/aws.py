import scrapy
from scrapy.loader import ItemLoader
from awscrawl.items import AwscrawlItem
from urllib import request
from urllib import error
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

class AwsSpider(scrapy.Spider):
    name = 'aws'
    allowed_domains = ['amazon.cn']
    start_urls = ['https://www.amazon.cn/']

    def start_requests(self):
        urls = [
            'https://www.amazon.cn/s?k=spark',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errback_httpbin,  dont_filter=True)

    def parse(self, response):
        for i in range(2,50):    
            l = ItemLoader(item=AwscrawlItem())   
            l.add_value('productName',response.xpath('//*[@id="search"]/div[1]/div[2]/div/span[3]/div[2]/div[%s]/div/span/div/div/div[2]/h2/a/span/text()'%(i)).get())
            l.add_value('productDetail',''.join(response.xpath('//*[@id="search"]/div[1]/div[2]/div/span[3]/div[2]/div[%s]/div/span/div/div/div[2]/div/span/text()'%(i)).getall()))
            priceXpath=['//*[@id="search"]/div[1]/div[2]/div/span[3]/div[2]/div[%s]/div/span/div/div/div[4]/div[1]/div/div/a/span/span[2]/span/text()'%(i),
                        '//*[@id="search"]/div[1]/div[2]/div/span[3]/div[2]/div[%s]/div/span/div/div/div[4]/div[2]/div/div/a/span/span[2]/span/text()'%(i)
                       ]
            for xpath in priceXpath:
                price =','.join(response.xpath(xpath).getall()).replace("￥,","￥")
                if price != None and len(price) > 0:
                    l.add_value('productPrice',price)
            yield l.load_item()
        next_page = response.xpath('//*[@id="search"]/div[1]/div[2]/div/span[3]/div[2]/div[50]/span/div/div/ul/li[7]/a/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)    
       

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)