import scrapy
from news_scraper.items import NewsScraperItem


class VenturebeatarticlesSpider(scrapy.Spider):
    name = "venturebeatarticles"
    allowed_domains = ["venturebeat.com"]
    start_urls = ["https://venturebeat.com/"]

    def parse(self, response):
        article_links = response.css("a.ArticleListing__title-link")
        yield from response.follow_all(article_links, self.parse_article)

    def parse_article(self, response):
        item = self.create_item(response)
        if item:
            yield item

    def create_item(self, response):
        title = response.css("h1.article-title::text").get()
        date = response.css("time.the-time::attr(datetime)").get()
        content = response.css("div.article-content > p::text, div.article-content > p > a::text").getall()
        content = " ".join(content)
        url = response.url

        if title and date and content and url:
            item = NewsScraperItem(title=title, date=date, content=content, url=url)
            return item
        else:
            self.logger.warning("Failed to extract data from %s", response.url)
