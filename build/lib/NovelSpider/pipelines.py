# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from scrapy.exporters import JsonItemExporter
from NovelSpider.tool.db import DBConfig
from .models.es_types import NovelType
from w3lib.html import remove_tags

class NovelspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    #自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('novel.json', 'w', encoding="utf-8")
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item
    def spider_closed(self, spider):
        self.file.close()


class MysqlPipeline(object):
    def __init__(self):
        self.db = DBConfig()

    def __del__(self):
        self.db.closeDB()

    def process_item(self, item, spider):
        insert_sql = """
            insert into xbiquge(tags, bookname, last_page, catalog, next_page, content)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        insertArr = {
            "tags":item["tags"],
            "bookname":item["bookname"],
            "last_page": item["last_page"],
            "catalog": item["catalog"],
            "next_page": item["next_page"],
            "content": item["content"]
        }
        sql = self.db.getInsertSql(insertArr, "xbiquge")
        self.db.insert(sql, False)


class JsonExporterPipeline(object):
    #调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('novelexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class ElasticsearchPipeline(object):
    #将数据写入到es中

    def process_item(self, item, spider):
        #将item转换为es的数据
        item.save_to_es()

        return item