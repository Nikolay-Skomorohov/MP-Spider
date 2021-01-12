# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Join, TakeFirst, Compose, MapCompose


class MpdataItem(scrapy.Item):
    """
    Defines the item fields and specifies processors for each field
    """

    name = scrapy.Field(
        input_processor=MapCompose(str.title, str.strip),
        output_processor=Join(' '),
    )
    image = scrapy.Field(
        output_processor=TakeFirst(),
    )
    birthdate = scrapy.Field(
        output_processor=TakeFirst(),
    )
    birthplace = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=Compose(lambda x: x[0] if len(x[0]) > 2 else "-"),
    )
    profession = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )
    languages = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=Join(', '),
    )
    party = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )
    electoral_district = scrapy.Field(
        output_processor=TakeFirst(),
    )
    first_time_mp = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=Join(', '),
    )
    email = scrapy.Field(
        output_processor=TakeFirst(),
    )
