# coding=UTF-8
import scrapy


class GooglePatentSpider(scrapy.Spider):
    name = "google_patent_spider"

    def start_requests(self):
        urls = [
            'https://www.google.com.tw/patents/US9000000?dq=9000000&hl=us',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        title = response.css('invention-title::text').extract()[0]
        abstract = response.css('div.abstract::text').extract()[0]
        bibdata = response.css('table.patent-bibdata tr')
        print title
        print '-----------------------'
        print abstract
        print '-----------------------'
        print bibdata
        print '-----------------------'
        print bibdata[0].css('td::text').extract()[0]
        print bibdata[0].css('td::text').extract()[1]
        tempdict = {'title':title, bibdata[0].css('td::text').extract()[0].encode('utf8'):bibdata[0].css('td::text').extract()[1]}
        print '-----------------------@@@'
        print tempdict