# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

class cdgasPipeline(object):
    def process_item(self, item, spider):
        file = open('items.json', 'a', encoding='utf-8')
        line = json.dumps(dict(item), ensure_ascii=False)+"\n"
        file.write(line)  # 以 json 的格式写入
        return item
