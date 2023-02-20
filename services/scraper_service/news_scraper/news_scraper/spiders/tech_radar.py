import scrapy
from news_scraper.items import NewsScraperItem


class TechRadarSpider(scrapy.Spider):
    name = "tech-radar"
    num_of_pages = 5
    allowed_domains = ["techradar.com"]
    start_urls = [f"https://www.techradar.com/news/{category}/page/{i}"
                  for i in range(1, num_of_pages+1)
                  for category in ["computing", "software", "phone-and-communications"]]
    
    def parse(self, response):
        for article_link in response.css("a.article-link::attr(href)").getall():
            yield response.follow(article_link, self.parse_article)

    def parse_article(self, response):
        title = response.css('header h1::text').get()
        content = " ".join(response.css("div#article-body > p::text, div#article-body > p > a::text, div#article-body > p > a > u::text").getall())
        date = response.css("time.relative-date::attr(datetime)").get()
        url = response.url

        item = NewsScraperItem(title=title, content=content, date=date, url=url)

        if item['title'] and item['date'] and item['url'] and item['content']:
            yield item
