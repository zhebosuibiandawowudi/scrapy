from datetime import datetime
from elasticsearch_dsl import Document, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class NovelType(Document):
    #新笔趣阁小说类型
    url = Keyword()
    suggest = Completion(analyzer=ik_analyzer)
    tags = Text(analyzer="ik_max_word")
    bookname = Text(analyzer="ik_max_word")
    content = Keyword()
    last_page = Keyword()
    catalog = Keyword()
    next_page = Keyword()

    class Index:
        name = "xbiquge"
        settings = {
            "number_of_shards": 5,
        }

#create the mappings in elasticsearch
if __name__ == "__main__":
    NovelType.init()