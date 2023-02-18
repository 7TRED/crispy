import scrapy
from news_scraper.items import NewsScraperItem


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


class TechRadarSpider(scrapy.Spider):
    name = "tech-radar"
    num_of_pages = 5
    allowed_domains = ["techradar.com"]

    start_urls = getPageUrls(num_pages=num_of_pages)

    def parse(self, response):
        article_links = response.css("a.article-link")
        return response.follow_all(article_links, self.parseArticle)

    def parseArticle(self, response):
        output = self._getContent(response)
        article = NewsScraperItem()
        article['title'] = output.get("title")
        article['content'] = output.get("body")
        article['url'] = response.url
        article['date'] = output.get("date")

        yield article


    def _getContent(self, response):
        header = response.css('header h1::text').get()
        body = response.css("div#article-body > p::text, div#article-body > p > a::text, div#article-body > p > a > u::text").getall()
        body = " ".join(body)
        article_time = response.css("time.relative-date::attr(datetime)").get()

        output = {}
        output["title"] = header
        output["body"] = body
        output["date"] = article_time

        return output