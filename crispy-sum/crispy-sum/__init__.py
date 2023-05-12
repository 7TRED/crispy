import logging
import traceback
from typing import List

import azure.functions as func
from torch.utils.data import DataLoader

from .summarizer import CrispySummarizer
from .article_pb2 import ArticleBatch
from .summary_pb2 import Summary, SummaryBatch


summarizer = CrispySummarizer()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def parse_request(req: func.HttpRequest) -> List[dict]:
    serializedString = req.get_body()
    article_list = ArticleBatch()
    article_list.ParseFromString(serializedString)

    return [
        {
            "content": article.content,
            "article_id": article.article_id,
            "title": article.title,
            "url": article.url,
            "date": article.date,
        }
        for article in article_list.articles
    ]


def generate_summaries(articles: List[dict]) -> str:
    summary_list = SummaryBatch()

    dataloader = DataLoader(articles, batch_size=3, shuffle=False)

    for batch in dataloader:
        summaries = summarizer(batch["content"])
        for i in range(len(batch["content"])):
            print(i)
            summary = Summary(
                article_id=batch["article_id"][i],
                summary=summaries[i],
                title=batch["title"][i],
                url=batch["url"][i],
                date=batch["date"][i],
            )
            summary_list.summaries.append(summary)
    return summary_list.SerializeToString()


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    req_body = req.get_body()

    logging.info("Request body: %s", req_body[:20])
    if req_body:
        try:
            articles = parse_request(req)
            summaries = generate_summaries(articles)
            headers = {
                "Content-Type": "text/plain",
                "Access-Control-Allow-Origin": "*",
            }
            return func.HttpResponse(
                summaries,
                headers=headers,
            )
        except Exception as e:
            print(traceback.format_exc())
            return func.HttpResponse(str(e), status_code=400)

    else:
        return func.HttpResponse(
            "Please pass an article in the request body", status_code=400
        )
