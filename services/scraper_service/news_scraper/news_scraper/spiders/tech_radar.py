import scrapy
import json
from bs4 import BeautifulSoup
from news_scraper.items import NewsScraperItem
from requests import get


def createUrls(page):
    categories = ["computing", "software", "phone-and-communications"]
    urls = []
    for category in categories:
        if page == 1:
            urls.append(f"https://www.techradar.com/news/{category}")
        else:
            urls.append(
                f"https://www.techradar.com/news/{category}/page/{page}")
    return urls


def getPageUrls(num_pages):
    output = []
    for i in range(1, num_pages+1):
        urls = createUrls(i)
        for url in urls:
            output.append(url)

    return output


def getContent(url):
    resp = get(url)
    soup = BeautifulSoup(resp.text, "lxml")
    header = soup.select('header h1')[0].getText()
    hawk = soup.select("div.hawk-title-container")
    body = soup.select("div#article-body")[0].getText().split("\n\n")[2]
    if len(hawk) > 0:
        body = body.split(hawk[0].getText())[0]
    article_time = soup.select("time.relative-date")[0]

    output = {}
    output["title"] = header
    output["body"] = body
    output["date"] = article_time.attrs.get("datetime")

    return output


class TechRadarSpider(scrapy.Spider):
    name = "tech-radar"
    num_of_pages = 5
    allowed_domains = ["techradar.com"]

    start_urls = getPageUrls(num_pages=num_of_pages)

    def parse(self, response):
        article_links = [a.attrib["href"]
                         for a in response.css("a.article-link")]

        for link in article_links:
            output = getContent(link)
            article = NewsScraperItem()
            article['title'] = output.get("title")
            article['content'] = output.get("body")
            article['url'] = link
            article['date'] = output.get("date")

            yield article
