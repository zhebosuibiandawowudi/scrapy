# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse

from NovelSpider.items import XbiqugeNovelItem
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy_redis.spiders import RedisSpider


# #redis
# class XbiqugeSpider(RedisSpider):
#     name = 'xbiquge'
#     allowed_domains = ['www.xbiquge.la']
#     redis_key = 'xbiquge:start_urls'
#
#     def parse(self, response):
#         # do stuff
#         pass

class XbiqugeSpider(scrapy.Spider):
    name = 'xbiquge'
    allowed_domains = ['www.xbiquge.la']
    start_urls = ['http://www.xbiquge.la/xiaoshuodaquan/']

    #获取动态网页内容
    # def __init__(self):
    #     self.browser = webdriver.Firefox(executable_path="C:/Users/zw/Downloads/geckodriver.exe")
    #     super(XbiqugeSpider, self).__init__()
    #     dispatcher.connect(self.spider_closed, signals.spider_closed)
    #
    # def spider_closed(self, spider):
    #     #当爬虫退出的时候关闭FireFox
    #     print("spider closed")
    #     self.browser.quit()

    #收集新笔趣阁所有404的页面数和url
    handle_httpstatus_list = [404]

    def __init__(self, **kwargs):
        self.fail_urls = []
        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
    def handle_spider_closed(self, spider, reason):
        self.crawler.stats.set_value("failed_urls", ",".join(self.fail_urls))

    def parse(self, response):
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        #解析所有小说列表url并交给目录页解析
        novel_lists = response.css("#main > .novellist a")
        for novel_list in novel_lists:
            novel_url = novel_list.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, novel_url), callback=self.parse_catalog)

    # 解析目录页中的所有章节url并交给scrapy下载后并进行解析
    def parse_catalog(self, response):
        list_nodes = response.css("#list a")
        for list_node in list_nodes:
            list_url = list_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, list_url), callback=self.parse_detail)

    def parse_detail(self, response):
        # print(response.url)
        novel_item = XbiqugeNovelItem()
        #章节url
        url = response.url
        #小说类别
        tags = response.css(".con_top > a::text").extract()[1]
        #小说名
        bookname = response.css(".con_top > a::text").extract()[2]
        #章节名称
        chapter = response.css(".bookname > h1 ::text").extract()[0]
        #提取出干净的纯文本小说内容
        content_list = response.css("#content").extract()
        content_str = "".join(content_list)
        content = re.sub('<\/div>', ' ', re.sub('<div id="content">', ' ', re.sub('<br>', ' ', re.sub('<p>([\w\W]*?)<\/p>', ' ', content_str))))
        #上一章、目录、下一章
        last_page = response.css(".bottem1 > a:nth-child(2) ::attr(href)").extract()[0]
        catalog = response.css(".bottem1 > a:nth-child(3) ::attr(href)").extract()[0]
        next_page = response.css(".bottem1 > a:nth-child(4) ::attr(href)").extract()[0]

        novel_item["bookname"] = bookname
        novel_item["tags"] = tags
        novel_item["url"] = url
        novel_item["chapter"] = chapter
        novel_item["content"] = content
        novel_item["last_page"] = last_page
        novel_item["catalog"] = catalog
        novel_item["next_page"] = next_page

        yield novel_item

