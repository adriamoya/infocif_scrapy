# -*- coding: utf-8 -*-
import os
import json
import time
import datetime
import scrapy
from scrapy.crawler import CrawlerProcess
from utils.functions import get_arguments, print_breakline
from infocif_scrapy.spiders.infocif_spider import InfocifSpider

if __name__ == '__main__':
    
    # Get arguments
    start_page, end_page, single_page = get_arguments()

    time.sleep(4)

    # Scraping process
    process = CrawlerProcess()
    process.crawl(InfocifSpider, start_page=start_page, end_page=end_page, single_page=single_page)
    process.start() # the script will block here until all crawling jobs are finished
