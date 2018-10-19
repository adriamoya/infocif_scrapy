# -*- coding: utf-8 -*-
import re
import scrapy

from scrapy.http.request import Request

from ..items import InfocifItem
from utils.functions import numberize

_url = 'https://www.infocif.es/ranking/ventas-empresas/espana?pagina='


class InfocifSpider(scrapy.Spider):

    def __init__(self, start_page=1, end_page=596, single_page=False):
        start_urls_list = []
        for page in range(start_page, end_page+1):
            start_urls_list.append('%s%s' % (_url, page))
            if single_page:
                break
        print(start_urls_list)
        self.start_urls = start_urls_list

    name = 'infocif'
    allowed_domains = ['infocif.es']
    custom_settings = {
		'ITEM_PIPELINES': {
			'infocif_scrapy.pipelines.ItemsPipeline': 400
		}
	}

    def parse(self, response):

        self.logger.info('parsing...')

        if response.status == 200:

            table = response.xpath('//table[@id="tablaranking"]')

            if table:
                keys = [th for th in table.xpath('.//th/text()').extract()]
                ventas_years = [
                    numberize(key) for key in keys if 'ventas' in key.lower()
                ]
                result_years = [
                    numberize(key) for key in keys if 'resultado' in key.lower()
                ]
                ebitda_years = [
                    numberize(key) for key in keys if 'ebitda' in key.lower()
                ]

                for row in table.xpath('./tbody//tr'):

                    company = InfocifItem()

                    # Initialize variables
                    name = None
                    ventas = []
                    resultado = None
                    ebitda = None
                    empleados = None
                    sector = None
                    municipio = None
                    provincia = None

                    # Parse list view
                    rank        = numberize(row.xpath('.//td[1]/text()').extract()[0].split()[0])
                    name        = row.xpath('.//td[2]/a/text()').extract()[0].strip().lower()
                    url_detail  = row.xpath('.//td[2]/a/@href').extract()[0]
                    ventas.append(numberize(row.xpath('.//td[3]/text()').extract()[0].strip()))
                    ventas.append(numberize(row.xpath('.//td[4]/text()').extract()[0].strip()))
                    resultado   = numberize(row.xpath('.//td[5]/text()').extract()[0].strip())
                    ebitda      = numberize(row.xpath('.//td[6]/text()').extract()[0].strip())
                    empleados   = numberize(row.xpath('.//td[7]/text()').extract()[0].strip())
                    sector      = row.xpath('.//td[8]/span/@title').extract()[0].strip()
                    try:
                        municipio   = row.xpath('.//td[9]/text()').extract()[0].strip().lower()
                    except:
                        pass
                    try:
                        provincia   = re.findall('(?!\()\w+(?=\))', row.xpath('.//td[9]/text()').extract()[1])[0].strip().lower()
                    except:
                        pass

                    company = {
                        'rank': rank,
                        'name': name,
                        'empleados': empleados,
                        'municipio': municipio,
                        'provincia': provincia,
                        'sector': sector,
                        'ebitda_%s' % ebitda_years[0]: ebitda,
                        'resultado_%s' % result_years[0]: resultado,
                        'ventas_%s' % ventas_years[0]: ventas[0],
                        'ventas_%s' % ventas_years[1]: ventas[1]
                    }

                    request = scrapy.Request(
                        url_detail,
                        callback=self.parse_detail,
                        dont_filter=True)
                    request.meta['item'] = company

                    yield request

    def parse_detail(self, response):

        # Initialize variables
        cp = None
        cif = None
        antig = None
        owner = None

        company = response.meta['item']

        if response.status == 200:

            for panel in response.xpath('//div[contains(@id, "fe-informacion-izq")]'):
                for strong in panel.xpath('.//strong'):
                    s = strong.xpath('./text()').extract()[0].strip().lower()
                    if 'cif' in s:
                        cif = strong.xpath('./following-sibling::h2/text()').extract()[0].strip()
                    if 'antigüedad' in s:
                        antig = numberize(strong.xpath('./following-sibling::p/text()').extract()[0].split()[0])
                    if 'cargos' in s:
                        owner = strong.xpath('./following-sibling::p/text()').extract()[0].strip()
                        owner = re.findall('.+?(?=\.)', owner)
                        if not owner:
                            owner = strong.xpath('./following-sibling::p/text()').extract()[0].strip()
                        else:
                            owner = owner[0]
                        owner = re.sub(
                            'ver más', '', owner,
                            flags=re.IGNORECASE).strip().lower()
                    if 'domicilio' in s:
                        cp = strong.xpath('./following-sibling::p/text()').extract()[0].strip()
                        cp = re.search('\d\d\d\d\d', cp)
                        if cp:
                            cp = cp.group(0)

            company['cif'] = cif
            company['cp'] = cp
            company['antig'] = antig
            company['owner'] = owner

            yield company
