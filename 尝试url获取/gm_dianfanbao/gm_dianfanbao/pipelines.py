# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import pymongo
from gm_dianfanbao import settings
from scrapy import signals
from scrapy.exporters import CsvItemExporter
from gm_dianfanbao.settings import FIELDS_TO_EXPORT
class GmDianfanbaoPipeline(object):
    def process_item(self, item, spider):
        return item
class CSVPipeline(object):

  def __init__(self):
    self.files = {}

  @classmethod
  def from_crawler(cls, crawler):
    pipeline = cls()
    crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
    crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
    return pipeline

  def spider_opened(self, spider):
    Time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    file = open('%s_国美电饭煲%s.csv' % (spider.name,Time), 'wb')
    self.files[spider] = file
    self.exporter = CsvItemExporter(file)
    self.exporter.fields_to_export = FIELDS_TO_EXPORT
    self.exporter.start_exporting()

  def spider_closed(self, spider):
    self.exporter.finish_exporting()
    file = self.files.pop(spider)
    file.close()

  def process_item(self, item, spider):
    self.exporter.export_item(item)
    return item
class MongoPipeline(object):
    def __init__(self):
        # 连接数据库
        self.client = pymongo.MongoClient(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
        self.db = self.client[settings.MONGO_DB]  # 获得数据库的句柄
        self.coll = self.db[settings.MONGO_COLL]  # 获得collection的句柄

    def process_item(self, item, spider):
        insert_item = dict(item)  # 把item转化成字典形式
        # 插入之前查询text是否存在，不存在的时候才插入。
        # self.coll.update({"ProductID": insert_item['ProductID']}, {'$setOnInsert': insert_item}, True)
        self.coll.insert(insert_item)  # 向数据库插入一条记录
        return item  # 会在控制台输出原item数据，可以选择不写