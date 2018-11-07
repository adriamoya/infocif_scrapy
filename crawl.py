# -*- coding: utf-8 -*-
import os
import json
import time
import datetime
import scrapy
import pandas as pd
from scrapy.crawler import CrawlerProcess
from utils.functions import get_arguments, print_breakline
from infocif_scrapy.spiders.infocif_spider import InfocifSpider

# nombre_url_list = [
# 'mercadona-sa',
# 'oliveras-&-sanz-sl',
# 'hotel-segle-xx-sl',
# 'armenvisu-sl',
# 'viatges-&-transports-pony-expressolsona-sl',
# 'glamour-tarrega-sl',
# 'ceba-sa',
# 'serovi-sl',
# 'flors-aglana-sl',
# 'cios-clinica-dental-slp',
# 'fusteria-oro-i-fills-sl']

if __name__ == '__main__':

    df = pd.read_csv('../output/empresas.csv', sep=';')
    # df[['nombre_url', 'provincia']].drop_duplicates().shape)
    nombre_url_list = list(df['nombre_url'].unique())

    print("There are %s companies" % len(nombre_url_list))

    # Get arguments
    single_page = get_arguments()

    time.sleep(4)

    # Scraping process
    process = CrawlerProcess()
    process.crawl(InfocifSpider, nombre_url_list=nombre_url_list, single_page=single_page)
    process.start() # the script will block here until all crawling jobs are finished
