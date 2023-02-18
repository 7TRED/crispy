import scrapy
from news_scraper.items import NewsScraperItem

class BgrindiaSpider(scrapy.Spider):
    name = "BGRIndia"
    allowed_domains = ["www.techlusive.in"]
    start_urls = ["https://www.techlusive.in/"]

    def parse(self, response):
        articleLinks=response.css("a.mob_text_ln_aLink::attr(href)").getall()
        return response.follow_all(articleLinks,self.parseArticle)
    
    def parseArticle(self,response):
        content=response.css("div.article-content > p::text").getall()
        content=" ".join(content)

        item=NewsScraperItem();
        item['title']=response.css("h1.title_name::text").get();
        item['content']=content;
        item['date']=response.css("li.publish>meta::attr(content)").get();
        item['url']=response.url;
        yield item;
