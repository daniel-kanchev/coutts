import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from coutts.items import Article


class CoutSpider(scrapy.Spider):
    name = 'cout'
    start_urls = ['https://www.coutts.com/insights.html']

    def parse(self, response):
        links = response.xpath('//h3[@class="searchResults-title"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="article-hero-title"]//text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="component-content metadata-date"]//text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%d %b %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[contains(@class, "richText component section grid_8 ")]/div[@class="component-'
                                 'content"]/div[@class="richText-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
