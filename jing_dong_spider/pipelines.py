# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from pymysql import err
from pymysql.err import IntegrityError


class MySQLPipeline(object):
    def __init__(self, mysql_config):
        self.mysql_config = mysql_config

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_config=crawler.settings.get('MYSQL_CONFIG')
        )

    def open_spider(self, spider):
        self.client = pymysql.connect(**self.mysql_config)
        self.cursor = self.client.cursor()

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        insert_sql = "INSERT INTO product_comments(product_id,product_name,product_comment) VALUES (%s,%s,%s)"
        try:
            self.cursor.execute(insert_sql, (item["product_id"], item["product_name"],
                                             item["product_comment"]))
            self.client.commit()
            return item
        except IntegrityError:
            spider.logger.info(
                "Duplicate entry '%s' for key 'PRIMARY'" % item["product_comment"])
