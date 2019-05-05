# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import redis
import scrapy
from scrapy.loader import ItemLoader
from .models.es_types import NovelType
from w3lib.html import remove_tags

from elasticsearch_dsl.connections import connections
es = connections.create_connection(NovelType)

redis_cil = redis.StrictRedis(host="localhost")

class NovelspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def gen_suggests(index, info_tuple):
    #根据字符串生成搜索建议数据
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            #调用es的analyze接口分析字符串
            words = es.indices.analyze(index="xbiquge", body={"analyzer":"ik_max_word", "text":"{0}".format(text)})
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words), "weight":weight})

    return suggests

class XbiqugeNovelItem(scrapy.Item):
    url = scrapy.Field()
    tags = scrapy.Field()
    bookname = scrapy.Field()
    content = scrapy.Field()
    last_page = scrapy.Field()
    catalog = scrapy.Field()
    next_page = scrapy.Field()

    def save_to_es(self):
        novel = NovelType()
        novel.url = self["url"]
        novel.tags = self["tags"]
        novel.bookname = self["bookname"]
        novel.content = remove_tags(self["content"])
        novel.last_page = self["last_page"]
        novel.catalog = self["catalog"]
        novel.next_page = self["next_page"]

        novel.suggest = gen_suggests(NovelType, ((novel.bookname,10),(novel.tags,7)))

        novel.save()
        redis_cil.incr("xbiquge_count")

        return