# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
from jsonschema import validate, ValidationError
from scrapy.exceptions import DropItem
import sqlite3


class MpdataPipeline:
    def process_item(self, item, spider):
        return item


class DefaultValuesPipeline:
    """
    Sets the default values for each item field.
    """
    def process_item(self, item, spider):
        item.setdefault('image', '-')
        item.setdefault('birthdate', '-')
        item.setdefault('birthplace', '-')
        item.setdefault('profession', '-')
        item.setdefault('languages', '-')
        item.setdefault('party', '-')
        item.setdefault('electoral_district', '-')
        item.setdefault('first_time_mp', '-')
        item.setdefault('email', '-')

        return item


class ValidateItemPipeline:
    """
    Performs json schema validation on each item based on the described schema
    """
    json_schema = {
        "$schema": "http://json-schema.org/draft/2019-09/schema#",
        "type": "object",
        "properties": {
            "birthdate": {"type": "string"},
            "birthplace": {"type": "string"},
            "electoral_district": {"type": "string"},
            "email": {"type": "string"},
            "first_time_mp": {"type": "string"},
            "image": {"type": "string"},
            "languages": {"type": "string"},
            "name": {"type": "string"},
            "party": {"type": "string"},
            "profession": {"type": "string"},
        },
        "required": [
            "birthdate",
            "birthplace",
            "electoral_district",
            "email",
            "first_time_mp",
            "image",
            "languages",
            "name",
            "party",
            "profession",
        ],
    }

    def process_item(self, item, spider):
        try:
            validate(instance=ItemAdapter(item).asdict(), schema=self.json_schema)
            return item
        except ValidationError as ex:
            raise DropItem(f'Invalid schema! {ex}')


class SQLitePipeline:
    """
    Creates an SQLite database and table.
    Inserts the passed item. If already present, skips the item.
    """
    def open_spider(self, spider):
        db_name = spider.settings.get('SQLITE_DB_NAME')

        self.db_conn = sqlite3.connect(db_name)
        self.db_cur = self.db_conn.cursor()

    def close_spider(self, spider):
        self.db_conn.commit()
        self.db_conn.close()

    def process_item(self, item, spider):
        self.insert_db(item)
        return item

    def insert_db(self, item):
        values = (
            item['name'],
            item['birthdate'],
            item['birthplace'],
            item['electoral_district'],
            item['email'],
            item['first_time_mp'],
            item['image'],
            item['languages'],
            item['party'],
            item['profession'],
        )

        create_sqlite_db = '''CREATE TABLE IF NOT EXISTS mp_info (
                                    name text PRIMARY KEY,
                                    birthdate text NOT NULL,
                                    birthplace text NOT NULL,
                                    electoral_district text NOT NULL,
                                    email text NOT NULL,
                                    first_time_mp text NOT NULL,
                                    image text NOT NULL,
                                    languages text NOT NULL,
                                    party text NOT NULL,
                                    profession text NOT NULL
                                )'''

        self.db_cur.execute(create_sqlite_db)
        try:

            insert_sql = 'INSERT INTO mp_info VALUES(?,?,?,?,?,?,?,?,?,?)'
            self.db_cur.execute(insert_sql, values)
        except sqlite3.IntegrityError:
            pass



