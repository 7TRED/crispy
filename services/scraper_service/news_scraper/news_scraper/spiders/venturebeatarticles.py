import scrapy
from news_scraper.items import NewsScraperItem


class VenturebeatarticlesSpider(scrapy.Spider):
    name = "venturebeatarticles"
    allowed_domains = ["venturebeat.com"]
    start_urls = ["http://venturebeat.com/"]

    def parse(self, response):
        articleLinks = response.css("a.ArticleListing__title-link");
        return response.follow_all(articleLinks, self.parseArticle);

    def parseArticle(self, response):

        content = response.css("div.article-content > p::text, div.article-content > p > a::text").getall()
        content = " ".join(content)

        item = NewsScraperItem()
        item['title'] = response.css("h1.article-title::text").get();
        item['date'] = response.css("time.the-time::attr(datetime)").get();
        item['content'] = content;
        item['url'] = response.url;

        yield item;