# -*- coding: utf-8 -*-
import re
import scrapy

from scrapy.http.request import Request

from ..items import InfocifItem
from utils.functions import numberize

_url = 'http://www.infocif.es/ficha-empresa/'


class InfocifSpider(scrapy.Spider):

    def __init__(self, nombre_url_list, single_page=False):
        start_urls_list = []
        for nombre_url in nombre_url_list:
            start_urls_list.append('%s%s' % (_url, nombre_url))
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

        if response.status == 200 and response.url != 'http://www.infocif.es/':

            company = InfocifItem()

            company = {
                'name': None,
                'cif': None,
                'antig': None,
                'cp': None,
                'empleados': None,
                'domicilio': None,
                'municipio': None,
                # 'provincia': None,
                'owner': None,
                'rank_ventas': None,
                'sector': None,
                'telefono': None
            }

            # Initialize variables
            name = None
            cif = None
            antig = None
            cp = None
            empleados = None
            domicilio = None
            municipio = None
            # provincia = None
            owner = None
            rank_ventas = None
            sector = None
            telefono = None

            company['url'] = response.url

            name = response.xpath('//h1[contains(@class, "title")]/text()').extract()[0].strip().lower()
            if name:
                company['name'] = name

            rank_ventas = numberize(response.xpath('//div[contains(@class, "hoverred")]/span/text()').extract()[0].strip())
            if rank_ventas:
                company['rank_ventas'] = rank_ventas

            for panel in response.xpath('//div[contains(@id, "fe-informacion-izq")]'):
                for strong in panel.xpath('.//strong'):
                    s = strong.xpath('./text()').extract()[0].strip().lower()
                    if 'cif' in s:
                        cif = strong.xpath('./following-sibling::h2/text()')
                        if cif:
                            cif = cif.extract()[0].strip()
                        else:
                            cif = None
                    if 'antigüedad' in s:
                        antig = numberize(strong.xpath('./following-sibling::p/text()').extract()[0].split()[0])
                    if 'teléfono' in s:
                        telefono = numberize(strong.xpath('./following-sibling::p/text()').extract()[0].split()[0])
                    if 'empleados' in s:
                        empleados = numberize(strong.xpath('./following-sibling::p/text()').extract()[0].split()[0])
                    if 'sector' in s:
                        sector = ' '.join(strong.xpath('./following-sibling::p/text()').extract()[0].split()).lower()
                        if sector == '-':
                            sector = None
                    if 'domicilio' in s:
                        domicilio = ' '.join(strong.xpath('./following-sibling::p/text()').extract()[0].split()).lower()
                        if domicilio == '-':
                            domicilio = None
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
                        domicilio = ' '.join(strong.xpath('./following-sibling::p/text()').extract()[0].split()).lower()
                        if domicilio == '-':
                            domicilio = None
                        # cp = strong.xpath('./following-sibling::p/text()').extract()[0].strip()
                        if domicilio:
                            cp = re.search('\d\d\d\d\d', domicilio)
                            if cp:
                                cp = cp.group(0)
                            municipio = re.findall('(?<=\().+?(?=\))', domicilio)
                            if municipio:
                                municipio = municipio[-1]

            company['cif'] = cif
            company['antig'] = antig
            company['cp'] = cp
            company['domicilio'] = domicilio
            company['empleados'] = empleados
            company['municipio'] = municipio
            company['owner'] = owner
            company['sector'] = sector
            company['telefono'] = telefono

            yield company
