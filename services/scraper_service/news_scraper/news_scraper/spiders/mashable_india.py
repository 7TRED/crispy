import scrapy
from news_scraper.items import NewsScraperItem

def getStartURLs(num_pages):
    return [f"https://in.mashable.com/tech/?page={page}&ist=broll" for page in range(1, num_pages + 1)];

class MashableIndiaSpider(scrapy.Spider):
    name = "mashable-india"
    num_pages = 5
    allowed_domains = ["in.mashable.com"]
    start_urls = getStartURLs(num_pages)

    def parse(self, response):
        articleLinks = response.css("li.blogroll > a");
        return response.follow_all(articleLinks, self.parseArticle);

    def parseArticle(self, response):
        title = response.css("h1#id_title::text").get()
        date = response.css("time::attr(datetime)").get()
        content = response.css("div#id_text > p::text, div#id_text > p > a::text").getall()
        content = " ".join(content);

        article = NewsScraperItem()
        article["title"] = title
        article["date"] = date
        article["content"] = content
        article["url"] = response.url

        yield article
