# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import logging

# useful for handling different item types with a single interface
import sys
import threading
from queue import Queue

import pika
import pymongo
from itemadapter import ItemAdapter
from news_scraper.items import NewsScraperItem
from scrapy.exceptions import DropItem, NotConfigured

from .rbmq.publisher import Publisher
from .rbmq.rbmqtypes import RMQMessage


class ItemValidationPipeline:

    REQUIRED_FIELDS = ["title", "date", "url", "content"]

    def process_item(self, item, spider):
        if not isinstance(item, NewsScraperItem):
            return item

        for field in self.REQUIRED_FIELDS:
            if not item[field]:
                raise DropItem(item)

        return item


class MongodbPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        if not self.mongo_uri:
            sys.exit("MONGO_URI is not set")

    @classmethod
    def from_crawler(cls, crawler):
        if crawler.settings.get("DISABLE_MONGO_PIPELINE"):
            # if pipeline is disabled, raise NotConfigured
            raise NotConfigured
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "items"),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, NewsScraperItem):
            # insert items according to date
            collection = item["date"].split("T")[0]

            # check if item with same url already exists
            # if it exists return item and don't insert it
            # else insert it
            old_item = self.db[collection].find_one({"url": item["url"]})
            if old_item:
                raise DropItem(item)

            # insert item
            id = self.db[collection].insert_one(ItemAdapter(item).asdict())

            item["article_id"] = str(id.inserted_id)

            return item


class MessageQueuePipeline:
    """
    A class for publishing messages to a RabbitMQ broker.
    """

    def __init__(
        self,
        rmq_host,
        rmq_port,
        rmq_user,
        rmq_pass,
    ):
        print("Initializing RMQ pipeline")
        self.rmq_host = rmq_host
        self.rmq_port = rmq_port
        self.rmq_user = rmq_user
        self.rmq_pass = rmq_pass
        self.rmq_queue = "article_queue"
        self.rmq_exchange = "article_exchange"
        self.rmq_routing_key = "scraped.article"
        self.rmq_exchange_type = "topic"
        self.queue = Queue()

        self.connect_params = pika.ConnectionParameters(
            host=self.rmq_host,
            port=self.rmq_port,
            credentials=pika.PlainCredentials(self.rmq_user, self.rmq_pass),
        )
        self.type_config = Publisher.PublisherTypeConfig(
            queue=self.rmq_queue,
            exchange_name=self.rmq_exchange,
            exchange_type=self.rmq_exchange_type,
            routing_key=self.rmq_routing_key,
            confirm_delivery=True,
        )
        if not self.rmq_host:
            sys.exit("RMQ_URI is not set")

    @classmethod
    def from_crawler(cls, crawler):
        if crawler.settings.get("DISABLE_RMQ_PIPELINE"):
            # if pipeline is disabled, raise NotConfigured
            raise NotConfigured
        return cls(
            rmq_host=crawler.settings.get("RMQ_HOST"),
            rmq_port=crawler.settings.get("RMQ_PORT", 5672),
            rmq_user=crawler.settings.get("RMQ_USER"),
            rmq_pass=crawler.settings.get("RMQ_PASS"),
        )

    def open_spider(self, spider):
        try:
            print("Connecting to RabbitMQ")
            self.publisher = Publisher(self.connect_params, self.type_config)
            self.publisher.connect()
            logging.info("Connected to RabbitMQ")
            threading.Thread(target=self.worker, daemon=True).start()
        except Exception as e:
            print(f"Error connecting to RabbitMQ: {e}")
            raise e

    def close_spider(self, spider):
        # wait for queue to be empty
        self.queue.join()
        # close connection
        self.publisher.close()

    def process_item(self, item, spider):
        try:
            if isinstance(item, NewsScraperItem):
                logging.info(f"Sending item to RabbitMQ: {item['url']}")
                rmq_message = RMQMessage(
                    payload=ItemAdapter(item).asdict(),
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        delivery_mode=2,
                        type=self.rmq_routing_key,
                    ),
                )

                self.queue.put(rmq_message)
                return item
        except Exception as e:
            print(f"Error sending item to RabbitMQ: {e}")
            raise e

    def worker(self):
        while True:
            try:
                message = self.queue.get()
                self.publisher.publish(message)
                self.queue.task_done()
            except Exception as e:
                logging.error(f"Error sending message to RabbitMQ: {e}")
                raise e


class NewsScraperPipeline:
    def process_item(self, item, spider):
        return item
