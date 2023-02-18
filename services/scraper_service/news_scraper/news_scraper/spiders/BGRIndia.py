import scrapy
from news_scraper.items import NewsScraperItem

def getStartUrls(num_pages):
    return [f"https://www.techlusive.in/news/page/{i}" for i in range(1,num_pages+1)]

class BgrindiaSpider(scrapy.Spider):
    name = "BGRIndia"
    num_pages=5
    allowed_domains = ["www.techlusive.in"]
    start_urls = getStartUrls(num_pages)

    def parse(self, response):
        articleLinks=response.css("div.media>div.media-left>a::attr(href)").getall()
        return response.follow_all(articleLinks,self.parseArticle)
    
    def parseArticle(self,response):
        content=response.css("div.article-content>p::text").getall()
        content=" ".join(content)

        item=NewsScraperItem();
        item['title']=response.css("h1::text").get();
        item['content']=content;
        item['date']=response.css("li.publish>meta::attr(content)").get();
        item['url']=response.url;
        yield item;
