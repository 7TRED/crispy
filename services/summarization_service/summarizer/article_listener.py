import datetime
import logging
import os
import re

import pika
import pymongo
import requests
import time
from summarizer.article_pb2 import Article, ArticleBatch
from summarizer.rbmq.listener import Listener
from summarizer.rbmq.publisher import Publisher
from summarizer.rbmq.rbmqtypes import RMQMessage
from summarizer.summary_pb2 import SummaryBatch
from summarizer.worker_queues import WorkerQueue


class ScrapedArticleListener:

    RMQ_HOST = os.environ.get("RMQ_HOST")
    RMQ_PORT = os.environ.get("RMQ_PORT")
    RMQ_USER = os.environ.get("RMQ_USER")
    RMQ_PASS = os.environ.get("RMQ_PASS")
    MONGO_URI = os.environ.get("MONGO_URI")
    MONGO_DB = os.environ.get("MONGO_DB")

    ## Listener config
    RMQ_LISTENER_QUEUE = "article_queue"
    RMQ_LISTENER_EXCHANGE = "article_exchange"
    RMQ_LISTENER_ROUTING_KEY = "scraped.article"

    ## Publisher config
    RMQ_PUBLISHER_QUEUE = "summary_queue"
    RMQ_PUBLISHER_EXCHANGE = "summary_exchange"
    RMQ_PUBLISHER_ROUTING_KEY = "summary.article"

    EXCHANGE_TYPE = "topic"
    BATCH_SIZE = 5

    API_URL = "http://host.docker.internal:7071/api/crispy-sum"

    def __init__(self):

        ## Set up logging
        self._log = logging.getLogger(__name__)
        self._log.setLevel(logging.INFO)

        self.summary_queue = WorkerQueue(
            num_workers=4, task_callback=self._fetch_summary
        )
        self.publisher_queue = WorkerQueue(
            num_workers=1, task_callback=self._store_summary
        )
        self._batch = []

        self._log.info(f"[{datetime.datetime.now()}]- [x] Starting listener...]")
        self._log.info(f"[{datetime.datetime.now()}]- [x] Connecting to MongoDB...]")
        ## Set up MongoDB connection
        self._mongo_client = pymongo.MongoClient(self.MONGO_URI)
        self._mongo_db = self._mongo_client[self.MONGO_DB]

        self._log.info(f"[{datetime.datetime.now()}]- [x] Connecting to RabbitMQ...]")
        ## Set up RabbitMQ connection
        self._connect_params = pika.ConnectionParameters(
            host=self.RMQ_HOST,
            port=self.RMQ_PORT,
            credentials=pika.PlainCredentials(self.RMQ_USER, self.RMQ_PASS),
        )

        self._listener_type_config = Listener.ListenerTypeConfig(
            queue=self.RMQ_LISTENER_QUEUE,
            exchange_name=self.RMQ_LISTENER_EXCHANGE,
            exchange_type=self.EXCHANGE_TYPE,
            routing_key=self.RMQ_LISTENER_ROUTING_KEY,
            prefetch_count=1,
        )
        self._publisher_type_config = Publisher.PublisherTypeConfig(
            queue=self.RMQ_PUBLISHER_QUEUE,
            exchange_name=self.RMQ_PUBLISHER_EXCHANGE,
            exchange_type=self.EXCHANGE_TYPE,
            routing_key=self.RMQ_PUBLISHER_ROUTING_KEY,
            confirm_delivery=True,
        )

        self._listener = Listener(
            connect_params=self._connect_params, type_config=self._listener_type_config
        )
        self._listener.on_message(message_callback=self._callback())

    def _preprocess_text(self, text):
        # Remove URLs
        text = re.sub(r"http\S+", "", text)
        # Remove HTML tags
        text = re.sub(r"<.*?>", "", text)
        # Remove non-ASCII characters
        text = re.sub(r"[^\x00-\x7F]+", " ", text)

        text = " ".join(text.split("\n"))
        # Remove extra whitespace
        text = " ".join(text.split())
        return text

    def _fetch_summary(self, article_batch):

        ## 1. Make a request to the summarization service
        article_list = ArticleBatch()
        for payload in article_batch:

            article = Article()
            article.article_id = payload.get("article_id")
            article.url = payload.get("url")
            article.title = payload.get("title")
            article.content = self._preprocess_text(payload.get("content"))
            article.date = payload.get("date")

            article_list.articles.append(article)

        ## 2. Serialze the article_list
        serialized_article_list = article_list.SerializeToString()

        self._log.info(
            f"[{datetime.datetime.now()}]- [x] Fetching summary for {len(article_list.articles)} articles...]"
        )
        ## 3. Make a request to the summarization service
        # write code to log the time take to fetch the summary
        start_time = time.time()

        response = requests.post(
            self.API_URL, data=serialized_article_list, timeout=1200
        )

        end_time = time.time()

        self._log.info(
            f"[{datetime.datetime.now()}]- [x] Time taken to fetch summary {end_time - start_time}]"
        )
        if response.status_code != 200:
            self._log.error(
                f"[{datetime.datetime.now()}]- [X] Error while fetching summary: {response.status_code}]"
            )
            return

        self._log.info(
            f"[{datetime.datetime.now()}]- [x] Summary fetched successfully...]"
        )

        ## 4. Deserialize the response
        summary_list = SummaryBatch()
        summary_list.ParseFromString(response.content)

        ## 5. Store the summary in the database
        if self.publisher_queue.status == WorkerQueue.Status.stopped:
            self.publisher_queue.start()

        self.publisher_queue.add_task(summary_list)

    def _store_summary(self, summaryBatch: SummaryBatch):
        ## 1. Store the summary in the database
        summaries = [
            {
                "article_id": summary.article_id,
                "summary": summary.summary,
                "date": summary.date,
                "url": summary.url,
                "title": summary.title,
            }
            for summary in summaryBatch.summaries
        ]

        self._publisher = Publisher(
            connect_params=self._connect_params, type_config=self._publisher_type_config
        )

        self._publisher.connect()

        for summary in summaries:
            collection = summary.get("date").split("T")[0]
            result = self._mongo_db[collection].insert_one(summary)
            summary_id = str(result.inserted_id)
            message = RMQMessage(
                payload={
                    "summary_id": summary_id,
                    "article_id": str(summary.get("article_id")),
                    "summary": summary.get("summary"),
                    "date": summary.get("date"),
                    "url": summary.get("url"),
                    "title": summary.get("title"),
                },
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type="application/json",
                ),
                mandatory=False,
            )

            self._log.info(f"[x] Publishing summary : {message.to_json()}]")

            self._publisher.publish(message)

            self._log.info(
                f"[{datetime.datetime.now()}]- [x] Published summary: {summary.get('article_id')}]"
            )

        self._publisher.close()

    def _callback(self):
        @Listener.RMQMessageCallback
        def _call(ch, method, message: RMQMessage, handle_nack):
            ## To-do
            payload = message.payload
            if not payload.get("content"):
                self._log.error(
                    f"[{datetime.datetime.now()}]- [X] Invalid payload: {payload}]"
                )
                handle_nack(ch, method.delivery_tag, requeue=False)
                return

            article = payload.get("content")
            self._log.info(
                f"[{datetime.datetime.now()}]- [x] Received article: {payload.get('url')}]"
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)

            if self.summary_queue.status == WorkerQueue.Status.stopped:
                self.summary_queue.start()

            ## 2. Make a request to the summarization service
            self._batch.append(payload)
            if len(self._batch) == self.BATCH_SIZE:
                self._log.info("[x] Batch size reached.")
                self.summary_queue.add_task([article for article in self._batch])
                self._batch = []

        return _call
