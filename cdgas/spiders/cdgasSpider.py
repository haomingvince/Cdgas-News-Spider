# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractor import LinkExtractor
from cdgas.items import cdgasItem
from scrapy.spiders import Rule
from pprint import pprint as pp
# http://www.cdgas.com/
# http://www.cdgas.com/information/notice/index.html


class cdgasSpider(scrapy.Spider):
    name = 'cdgas'
    start_urls = ['http://www.cdgas.com/']
    news_type = {"notice": "重要通知", "gasstop": "停气信息", "news": "新闻动态", "zhaobiaogonggao": "招标公告", "zhaopinxinxi": "招聘信息"}

    def parse(self, response): # 进入官网，再分别进入各项分类
        for ntype in self.news_type.keys():
            url = "http://www.cdgas.com/information/" + ntype + "/index.html"
            yield scrapy.Request(url, callback=self.parse_pages)
    
    def parse_pages(self, response): # 进入分类
        ''' # For test. Parse only one page once
        url = response.url + "?currentPage=1"
        yield scrapy.Request(url, callback=self.parse_list)
        '''
        maxPage = 0
        content = response.css(".pager")
        for href in content.css("a::attr(href)").extract():   # 找到当前分页的最大页码
            temp = int(re.findall(r"\d+", href)[0])
            if temp >= maxPage:
                maxPage = temp
        for i in range(1, maxPage+1):   # 进入每一个页码页面
            url = response.url + "?currentPage=" + str(i)
            yield scrapy.Request(url, callback=self.parse_list)

    def parse_list(self, response):   # 爬取新闻链接
        content = response.css("#type-list-right")
        for href in content.css("a::attr(href)").extract():
            try:
                temp = re.match(r"/information/(\w+)/(\d+)/index\.html\?index\=(\d+)", href)
                print("parsed:", temp.group(0))
                url = "http://www.cdgas.com" + temp.group(0)
                yield scrapy.Request(url, callback=self.parse_news)
            except:
                print("filtered: ", href)
                continue

    def parse_news(self, response):   # 获得新闻正文以及相关数据
        item = cdgasItem()
        print("\nNow parsing: {}\n".format(response.url))
        try:
            temp = re.match(r"(.*)/information/(\w+)/(\d+)/index\.html\?index\=(\d+)", response.url)
            item["type"] = self.news_type[temp.group(2)]
        except:
            item["type"] = "---"
        content_temp = response.xpath('//*[@id="news-content"]/p/text() | //*[@id="news-content"]/p/strong/text() | //*[@id="news-content"]/p/span/text() | //*[@id="news-content"]/text()').extract()
        for i in range(len(content_temp)):
            content_temp[i] = content_temp[i].replace(u'\xa0', u' ').strip()
        item["title"] = response.css("div > h1.news-content-title::text").extract_first()
        item['url'] = str(response.url)
        try:
            item["time"] = re.findall(r"\d{4}-\d{2}-\d{2}", response.css("div > span.news-content-time::text").extract_first())[0]
        except:
            item["time"] = response.css("div > span.news-content-time::text").extract_first()
        item["content"] = "".join(content_temp)
        
        
        item["source"] = "---"
        return item