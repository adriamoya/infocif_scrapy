# -*- coding: utf-8 -*-
import re
import scrapy

from scrapy.http.request import Request

from ..items import InfocifItem
from utils.functions import numberize

_url = 'http://www.infocif.es/ficha-empresa/'
_url_cuentas = 'http://www.infocif.es/balance-cuentas-anuales/'


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

            company['slug'] = response.url.split('/')[-1]

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

            # yield company

            request = scrapy.Request(
                '%s%s' % (_url_cuentas, company['slug']),
                callback=self.parse_cuentas,
                dont_filter=True)
            request.meta['item'] = company

            yield request

    def parse_cuentas(self, response):

        self.logger.info('Parsing cuentas...')

        company = response.meta['item']

        try:

            # determinar si las cuentas estan en miles o no
            miles = response.xpath('//th[contains(text(),"Cuenta de resultados")]/text()')[0].extract()
            miles = re.findall('(miles)', miles)

            year_list				= response.xpath('//th[contains(text(),"Cuenta de resultados")]')[0].xpath('./following-sibling::th/span/text()')
            ingresos_expl_list  	= response.xpath('//td[contains(text(),"Ingresos de expl")]/following-sibling::td/text()')
            amortizaciones_list 	= response.xpath('//td[contains(text(),"Amortiz")]/following-sibling::td/span/text()')

            resultado_expl_list 	= response.xpath('//td[contains(text(),"Resultado de explotaci")]/following-sibling::td')
            total_activo_list 		= response.xpath('//td[contains(text(),"Total activo")]/following-sibling::td/text()')
            patrimonio_neto_list 	= response.xpath('//td[contains(text(),"Patrimonio neto")]/following-sibling::td/text()')
            deudas_cp_list			= response.xpath('//td[contains(text(),"Deudas a corto plazo")]/following-sibling::td/text()')
            deudas_lp_list			= response.xpath('//td[contains(text(),"Deudas a largo plazo")]/following-sibling::td/text()')
            deudores_comerc_list 	= response.xpath('//td[contains(text(),"Deudores comerciales")]/following-sibling::td/text()')
            acreedores_comerc_list 	= response.xpath('//td[contains(text(),"Acreedores comerciales")]/following-sibling::td/text()')


            if year_list:

                cuentas = []

                # para cada ejercicio
                for i in range(0, len(year_list), 1):

                    year = int(year_list[i].extract())

                    if miles:

                        self.logger.info('Cuentas de resultados en miles de euros ........................')

                        # cuenta de resultados
                        # --------------------------------------------------------

                        # ingresos de explotacion
                        ingresos_expl = ''.join(re.findall('[0-9]', ingresos_expl_list[i].extract()))
                        if ingresos_expl:
                            ingresos_expl = float(ingresos_expl)*1000
                        else:
                            ingresos_expl = 0

                        # amortizaciones
                        amortizaciones = ''.join(re.findall('[0-9]', amortizaciones_list[i].extract()))
                        if amortizaciones:
                            amortizaciones = float(amortizaciones)*(1000)
                        else:
                            amortizaciones = 0

                        # resultado de explotacion
                        if resultado_expl_list[i].xpath('./span[contains(@class,"rojo")]'):
                            # negativo
                            resultado_expl = ''.join(re.findall('[0-9]',resultado_expl_list[i].xpath('./span/text()').extract()[0]))
                            if resultado_expl:
                                resultado_expl = float(resultado_expl)*(-1000)
                            else:
                                resultado_expl = 0
                        else:
                        # positivo
                            resultado_expl = ''.join(re.findall('[0-9]',resultado_expl_list[i].xpath('./text()').extract()[0]))
                            if resultado_expl:
                                resultado_expl = float(resultado_expl)*(1000)
                            else:
                                resultado_expl = 0

                        # ebitda
                        ebitda = resultado_expl + amortizaciones

                        # balance
                        # --------------------------------------------------------
                        # total activo
                        total_activo = ''.join(re.findall('[0-9]',total_activo_list[i].extract()))
                        if total_activo:
                            total_activo = float(total_activo)*1000
                        else:
                            total_activo = 0

                        # patrimonio neto
                        patrimonio_neto = ''.join(re.findall('[0-9]',patrimonio_neto_list[i].extract()))
                        if patrimonio_neto:
                            patrimonio_neto = float(patrimonio_neto)*1000
                        else:
                            patrimonio_neto = 0

                        # deudas a corto plazo
                        deudas_cp = ''.join(re.findall('[0-9]',deudas_cp_list[i].extract()))
                        if deudas_cp:
                            deudas_cp = float(deudas_cp)*1000
                        else:
                            deudas_cp = 0

                        # deudas a largo plazo
                        deudas_lp = ''.join(re.findall('[0-9]',deudas_lp_list[i].extract()))
                        if deudas_lp:
                            deudas_lp = float(deudas_lp)*1000
                        else:
                            deudas_lp = 0

                        # deudores comerciales
                        deudores_comerc = ''.join(re.findall('[0-9]',deudores_comerc_list[i].extract()))
                        if deudores_comerc:
                            deudores_comerc = float(deudores_comerc)*1000
                        else:
                            deudores_comerc = 0

                        # acreedores comerciales
                        acreedores_comerc = ''.join(re.findall('[0-9]',acreedores_comerc_list[i].extract()))
                        if acreedores_comerc:
                            acreedores_comerc = float(acreedores_comerc)*1000
                        else:
                            acreedores_comerc = 0

                    else:

                        self.logger.info('Cuentas de resultados en euros ........................')

                        # cuenta de resultados
                        # --------------------------------------------------------

                        # ingresos de explotacion
                        ingresos_expl = float(''.join(re.findall('[0-9]', ingresos_expl_list[i].extract())))

                        # amortizaciones
                        amortizaciones = float(''.join(re.findall('[0-9]', amortizaciones_list[i].extract())))

                        # resultado de explotacion
                        if resultado_expl_list[i].xpath('./span[contains(@class,"rojo")]'):
                            # negativo
                            resultado_expl = float(''.join(re.findall('[0-9]', resultado_expl_list[i].xpath('./span/text()').extract()[0])))*(-1)
                        else:
                            # postivio
                            resultado_expl = float(''.join(re.findall('[0-9]', resultado_expl_list[i].xpath('./text()').extract()[0])))

                        # ebitda
                        ebitda = resultado_expl + amortizaciones

                        # balance
                        # --------------------------------------------------------

                        # total activo
                        total_activo = float(''.join(re.findall('[0-9]', total_activo_list[i].extract())))

                        # patrimonio neto
                        patrimonio_neto = float(''.join(re.findall('[0-9]', patrimonio_neto_list[i].extract())))

                        # deudas a corto plazo
                        deudas_cp = float(''.join(re.findall('[0-9]', deudas_cp_list[i].extract()))) # deudas total

                        # deudas a largo plazo
                        deudas_lp = float(''.join(re.findall('[0-9]', deudas_lp_list[i].extract()))) # deudas total

                        # deudores comerciales
                        deudores_comerc = float(''.join(re.findall('[0-9]', deudores_comerc_list[i].extract()))) # clientes

                        # acreedores comerciales
                        acreedores_comerc 	= float(''.join(re.findall('[0-9]', acreedores_comerc_list[i].extract()))) # proveedores


                    cuenta = {
                        'year': year,
                        'ingresos_expl': ingresos_expl,
                        'amortizaciones': amortizaciones,
                        'resultado_expl': resultado_expl,
                        'ebitda': ebitda,
                        'total_activo': total_activo,
                        'patrimonio_neto': patrimonio_neto,
                        'deudas_cp': deudas_cp,
                        'deudas_lp': deudas_lp,
                        'deudas_total': deudas_cp + deudas_lp,
                        'clientes': deudores_comerc,
                        'proveedores': acreedores_comerc
                        }
                    self.logger.info(cuenta)

                    cuentas.append(cuenta)

                company['cuentas'] = cuentas

        except:
            pass

        yield company
