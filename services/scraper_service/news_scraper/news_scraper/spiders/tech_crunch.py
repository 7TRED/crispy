import scrapy
import json
from bs4 import BeautifulSoup
from news_scraper.items import NewsScraperItem

def getPageUrl(page):
        return f"https://techcrunch.com/wp-json/tc/v1/magazine?page={page}&_embed=true&_envelope=true&categories=20429&cachePrevention=0"


class TechCrunchSpider(scrapy.Spider):
    name = "tech-crunch"
    num_of_pages = 5
    allowed_domains = ["techcrunch.com"]
    start_urls = [getPageUrl(i) for i in range(1,num_of_pages+1 )]

    def parse(self, response):
        cleanResponse = response.text.replace("/**/_jsonp_0(", "")
        cleanResponse = cleanResponse.replace(")","")
        jsonResponse = json.loads(cleanResponse)

        for item in jsonResponse['body'] :
            article = NewsScraperItem()
            soup = BeautifulSoup(item['content']['rendered'], 'lxml')
            content = "".join([tag.get_text() for tag in soup.find_all('p')])

            article['title'] = item['title']['rendered']
            article['content'] = content
            article['url'] = item['link']
            article['date']= item['date']

            yield article
