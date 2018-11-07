# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
# from scrapy import signals
# from scrapy.xlib.pydispatch import dispatcher

class ItemsPipeline(object):

    def __init__(self):
        self.file = codecs.open('./output/companies.json', 'w', encoding='utf-8')
        # dispatcher.connect(self.spider_closed, signals.spider_closed)

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()
