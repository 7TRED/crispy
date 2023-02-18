# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sys
import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import NotConfigured
from news_scraper.items import NewsScraperItem


class MongodbPipeline:
    
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        if not self.mongo_uri:
            sys.exit('MONGO_URI is not set')

    @classmethod
    def from_crawler(cls, crawler):
        if crawler.settings.get('DISABLE_MONGO_PIPELINE'):
            # if pipeline is disabled, raise NotConfigured
            raise NotConfigured
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, NewsScraperItem): 
            # insert items according to date
            collection = item['date'].split('T')[0]
            
            # check if item with same url already exists
            # if it exists return item and don't insert it
            # else insert it
            old_item = self.db[collection].find_one({'url': item['url']})
            if(old_item):
                return item
            
            # insert item
            self.db[collection].insert_one(ItemAdapter(item).asdict())

            return item


class NewsScraperPipeline:
    def process_item(self, item, spider):
        return item
