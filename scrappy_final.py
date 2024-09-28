from scrapy.crawler import CrawlerProcess
import scrapy
import os
import logging

class BookingSpider(scrapy.Spider):
    name = 'nested_spider'
    start_urls = [
        'https://www.booking.com/searchresults.en-gb.html?ss=Avignon'
    ]

    def parse(self, response):
        for i in range(3, 13, 2):
            item = {
                'city': response.xpath('/html/body/div[4]/div/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[3]/div[{}]/div[1]/div[2]/div/div/div[1]/div/div[2]/div/a/span/span[1]/text()'.format(i)).get(),
                'name': response.xpath('/html/body/div[4]/div/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[3]/div[{}]/div[1]/div[2]/div/div/div[1]/div/div[1]/div/h3/a/div[1]/text()'.format(i)).get(),
                'user_reviews': response.xpath('/html/body/div[4]/div/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[3]/div[{}]/div[1]/div[2]/div/div/div[2]/div/div[1]/a/span/div/div[1]/text()'.format(i)).get(),
                'url': response.xpath('/html/body/div[4]/div/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[3]/div[{}]/div[1]/div[2]/div/div/div[1]/div/div[1]/div/h3/a'.format(i)).css('::attr(href)').get(),
                'description': response.xpath('/html/body/div[4]/div/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[3]/div[{}]/div[1]/div[2]/div/div/div[1]/div/div[3]/text()'.format(i)).get(),
            }

            url = item['url']
            if url:
                yield response.follow(url, callback=self.parse_nested_page, meta={'item': item})

    def parse_nested_page(self, response):
        item = response.meta['item']
        item['hotel_gps'] = response.xpath('/html/body/div[4]/div/div[4]/div[1]/div[1]/div[1]/div[1]/div[3]/div[4]/p/a').css('::attr(data-atlas-latlng)').get()
        yield item

# Name of the file where the results will be saved
filename = "Booking_nested_top5.json"

# Ensure 'src/' directory exists
os.makedirs('src', exist_ok=True)

# If file already exists, delete it before crawling (because Scrapy will concatenate the last and new results otherwise)
if filename in os.listdir('src/'):
    os.remove('src/' + filename)

# Declare a new CrawlerProcess with some settings
process = CrawlerProcess(settings={
    'USER_AGENT': 'Chrome/126.0.0.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        'src/' + filename: {"format": "json"},
    }
})

# Start the crawling using the spider you defined above
process.crawl(BookingSpider)
process.start()
