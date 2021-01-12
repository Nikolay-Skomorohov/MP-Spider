import datetime

from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider
from scrapy.loader import ItemLoader
from MPdataCrawl.items import MpdataItem


class ParliamentMembersSpider(Spider):
    """
    The spider crawls the MP data.
    Crawling stops if encounters KeyError.
    Probable cause is a CAPTCHA user validation form.
    """
    name = 'mpdata'

    start_urls = [
        'https://www.parliament.bg/bg/MP',
    ]

    custom_settings = {
        'FEED_URI': 'mpdata_' + str(datetime.date.today()) + '.json',
        'FEED_FORMAT': 'json',
        'FEED_EXPORTERS': {
            'json': 'scrapy.exporters.JsonItemExporter',
        },
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def parse(self, response):
        """
        Goes to 'https://www.parliament.bg/bg/MP'.
        Gets all MP elements and loops them.
        Call the parse_details with the link for more MP info.
        """
        mp_list = response.css('div.MPBlock')
        for mp in mp_list:
            info_link = mp.css('div.MPinfo a').attrib['href']
            mp_details = Request(response.urljoin(info_link), callback=self.parse_details)

            yield mp_details

    def parse_details(self, response):
        """
        Creates a MpdataItem object and get the MP data list.
        Loops the 'li' elements and matches them to the item schema.
        Performs basic transformation on each iteration.
        """
        mp_loader = ItemLoader(MpdataItem(), response)

        mp_loader.add_css('name', 'div.MProwD strong:nth-child(1)::text')
        mp_loader.add_css('name', 'div.MProwD::text')
        mp_loader.add_css('name', 'div.MProwD strong:nth-child(2)::text')
        try:
            mp_loader.add_value('image', response.urljoin(response.css('div.MPBlock_columns2 > img').attrib['src']))
        except KeyError:
            raise CloseSpider('The spider encountered a CAPTCHA user validation form. Crawling aborted.')

        mp_info_list = response.css('ul.frontList li')

        for row in mp_info_list:
            row_text = row.get().lower()
            if "дата на раждане" in row_text:
                mp_loader.add_value('birthdate', row.re(r'\d{2}/\d{2}/\d{4}'))
                mp_loader.add_value('birthplace', row.re(r'(?<=\d{2}/\d{2}/\d{4} )\D+(?=<\D+>){1}'))
            elif "професия" in row_text:
                mp_loader.add_value('profession', row.re(r'(?<=: ){1}\w{1,}(?=;){1}|(?<=: ){1}\w{1,}'))
            elif "езици" in row_text:
                mp_loader.add_value('languages', row.re(r'((?<=: |; ){1}\w{1,}(?=;){1})|(?<=: |; ){1}\w{1,}'))
            elif "избран(а) с политическа сила" in row_text:
                mp_loader.add_value('party', row.re(r'(?<=: ){1}\D+(?=\d){0,}'))
            elif "изборен район" in row_text:
                mp_loader.add_value('electoral_district', row.re(r'(?<=: ){1}.+(?=;){1}'))
            elif "участие в предишно" in row_text:
                mp_loader.add_value('first_time_mp', row.css('a::text').get())
            elif "mail" in row_text:
                mp_loader.add_value('email', row.css('a::text').get())

        return mp_loader.load_item()
