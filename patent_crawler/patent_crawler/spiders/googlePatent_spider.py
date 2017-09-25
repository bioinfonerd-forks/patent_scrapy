# coding=UTF-8
import scrapy
import json
import pymongo
from pymongo import MongoClient


class GooglePatentSpider(scrapy.Spider):
    name = "google_patent_spider"

    def start_requests(self):
        urls = ['https://www.google.com.tw/patents/US'+str(pnumber)+'?dq='+str(pnumber)+'&hl=en-us'\
                 for pnumber in range(9000000, 9000100)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        #this section is used to crawl some unstructured data
        title = response.css('invention-title::text').extract()[0].encode('utf8')
        abstract = response.css('div.abstract::text').extract()[0].encode('utf8')
        result = {"Title":title, "Abstract": abstract}
        description = response.css('div.description > p, div.description > heading')
        description_list = list()
        changeH = 1
        heading = str()
        paragraph = str()
        for des in description:
            if len(des.css('heading::text').extract()) > 0:
                if changeH < 1:
                    description_list.append({"Heading": heading, "Paragraph": paragraph})
                changeH = 1
                heading = des.css('heading::text').extract_first()
            else:
                if changeH == 0:
                    paragraph += des.css('p::text').extract_first()
                else:
                    paragraph = des.css('p::text').extract_first()
                    changeH = 0
        result.update({"Description": description_list})
        claim_list = list()
        claim = response.css('div.patent-text > div.claims > div.claim > div.claim, div.patent-text > div.claims > div.claim-dependent')
        for cl in claim:
            if len(cl.css('div.claim-dependent').extract()) < 1:
                claim_content = ' '.join(cl.css('div.claim-text::text').extract()).replace('\n', '')
                claim_list.append({"Claim_content": claim_content, "Claim_reference":''})
            else:
                claim_content = cl.css('div.claim-text::text').extract()
                ref = cl.css('div.claim-text > claim-ref::text').extract_first()
                claim_content = ref.join(claim_content).replace('\n', '')
                claim_list.append({"Claim_content": claim_content, "Claim_reference": ref})

        result.update({"Claim": claim_list})
        # this section is used to process the bibilography data
        bibdata = response.css('table.patent-bibdata tr')
        required_bib_list = ['Publication number', 'Publication type', 'Application number', 'PCT number',\
                         'Publication date', 'Filling date', 'Priority date', 'Also published as', 'inventors',\
                         'Original Assignee', 'Export Citation']
        multichild_bib_list = ['Also published as', 'Original Assignee', 'Export Citation']
        for bib in bibdata:
            class_attr = bib.css('tr::attr(class)').extract()
            if len(class_attr) > 0 :
                class_attr = class_attr[0].split(' ')
            else:
                class_attr = list()
            tempbib = bib.css('td::text').extract()
            if 'alternate-patent-number' not in class_attr and len(tempbib) > 0 and tempbib[0] in required_bib_list :
                if tempbib[0] in multichild_bib_list:
                    multichild = bib.css('td span a::text').extract()
                    multichild = [item.encode('utf8') for item in multichild]
                    result.update({tempbib[0].encode('utf8'):multichild})
                else:
                    result.update({tempbib[0].encode('utf8'): tempbib[1].encode('utf8')})

        uri = "mongodb://ehang:12345677@140.117.69.70:30241/Pattern"
        client = MongoClient(uri)
        db = client.Pattern
        collection = db.google_patent
        collection.insert(result)
        # print json.dumps(result)



