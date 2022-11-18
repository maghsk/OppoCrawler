# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .items import *
import pymongo
import json
import dataclasses
import logging
import cachetools
from pathlib import Path

from scrapy.exporters import JsonLinesItemExporter


class WebGLPipeline:
    OUTPUT_BASE_PATH = Path('/home/ec2-user/OppoCrawler/output')

    def __init__(self):
        self.js_fp = None
        self.html_fp = None
        self.js_exporter = None
        self.html_exporter = None

    def process_item(self, item, spider):
        if isinstance(item, JavaScriptData):
            return self.process_js(item, spider)
        elif isinstance(item, HtmlData):
            return self.process_html(item, spider)

    def open_spider(self, spider):
        self.OUTPUT_BASE_PATH.mkdir(parents=True, exist_ok=True)
        self.html_fp = open(self.OUTPUT_BASE_PATH / 'simplified_html.json', 'wb')
        self.js_fp = open(self.OUTPUT_BASE_PATH / 'simplified_js.json', 'wb')

        self.html_exporter = JsonLinesItemExporter(
            self.html_fp,
            fields_to_export=['access_time', 'url', 'lit_used_webgl', 'lit_used_getcontext',
                              'remote_js_url_list'])

        self.js_exporter = JsonLinesItemExporter(
            self.js_fp,
            fields_to_export=['access_time', 'url', 'lit_used_webgl', 'lit_used_getcontext'])

    def close_spider(self, spider):
        self.html_exporter.finish_exporting()
        self.js_exporter.finish_exporting()

        self.html_fp.close()
        self.js_fp.close()

    def process_js(self, item: JavaScriptData, spider):
        self.js_exporter.export_item(item)
        return item

    def process_html(self, item: HtmlData, spider):
        self.html_exporter.export_item(item)
        return item


class MongoPipeline:
    js_collection_name = "js_col"
    html_collection_name = "html_col"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.js_col = self.db[self.js_collection_name]
        self.html_col = self.db[self.html_collection_name]
        self.js_cache = cachetools.FIFOCache(10_000_000)
        self.html_cache = cachetools.FIFOCache(10_000_000)
        for x in self.js_col.find({}, {"url": 1, "access_time": 1}):
            self.js_cache[x.get("url")] = x.get("access_time")
        for x in self.html_col.find({}, {"url": 1}):
            self.html_cache[x.get("url")] = x.get("access_time")

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, JavaScriptData):
            return self.hyd_process(item, self.js_col, self.js_cache)
        elif isinstance(item, HtmlData):
            return self.hyd_process(item, self.html_col, self.html_cache)
        else:
            raise ValueError()

    def hyd_process(self, item, col, cache):
        in_cache = item.url in cache

        if (not in_cache) and (col.find_one({"url": item.url}) is None):
            col.insert_one(dataclasses.asdict(item))
        else:
            logging.warning(f"Duplicated item, skip storing. URL: {item.url}. In_Cache: {in_cache}.")
        cache[item.url] = True
        return item
