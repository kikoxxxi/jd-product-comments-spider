# -*- coding: utf-8 -*-

__author__ = 'kikoxxxi'

import re
import json
import time
import math
import random
import scrapy
from scrapy import Request
from ..items import JingDongSpiderItem


class ProductCommentsSpider(scrapy.Spider):
    name = "product_comments_spider"
    sortType = 6  # 按时间排序 sortType=6
    score = [1, 2, 3]  # 差评 score=1,中评 score=2,好评 score=3
    product_name = input("Input the product's name: ").strip()  # iphone6
    product_id = input("Input the product's ID: ").strip()  # 4586850
    # 中差评的数量，空格隔开
    # 9100 6400
    counts_str = list(input("Input poor, general count: ").split())
    counts = map(lambda x: int(x), counts_str)
    # 根据好评默认只能爬100页，中差评的数量来确定要爬取的页数，最多爬取总页数的百分之六十八
    values = list(map(lambda c: math.ceil(c * 0.068), counts))
    values.append(100)
    page_nums = dict(zip(score, values))
    start_url = "https://item.jd.com/{}.html".format(product_id)

    def start_requests(self):
        return [Request(url=self.start_url, callback=self.parse)]

    def parse(self, response):
        html_content = response.text
        commentVersion = re.search(
            r"commentVersion:(.*?),", html_content).group(1).replace("'", "")
        delete_str = "fetchJSON_comment98vv{}(".format(commentVersion)
        # 切换中好差评url
        for score_num in self.score:
            # 翻页
            for page_num in range(self.page_nums[score_num]):
                comment_url = "https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv{}&productId={}&score={}&sortType={}&page={}&pageSize=10&isShadowSku=0&fold=1".format(
                    commentVersion, self.product_id, score_num, self.sortType, page_num)
                sec = random.randint(2, 12)
                time.sleep(sec)  # 防止被ban
                yield Request(url=comment_url, callback=self.parse_detail, meta={"delete_str": delete_str})

    def parse_detail(self, response):
        html_content = response.text
        delete_str = response.meta["delete_str"]
        # 清理数据即开头多余部分以及最后的分号和括号，并转成dict
        json_data = json.loads(html_content.replace(
            delete_str, "")[:-2], encoding="utf-8")
        comments = json_data["comments"]
        item = JingDongSpiderItem()
        for comment in comments:
            product_comment = comment["content"] if comment["content"] != "此用户未填写评价内容" else ""
            try:
                # 追评
                product_after_comment = comment["afterUserComment"]["hAfterUserComment"]["content"]
            except KeyError:
                product_after_comment = ""
            product_comment_list = [product_comment, product_after_comment]
            for pc in product_comment_list:
                if pc:
                    item["product_name"] = self.product_name
                    item["product_id"] = self.product_id
                    item["product_comment"] = self.delete_redundant_symbol(pc)
                    yield item

    def delete_redundant_symbol(self, data):
        # 去掉类似&hellip;\n多余的字符
        patterns = [re.compile(r"&[a-z+]+?;"), re.compile(r"[\n\r\s\t]")]
        for pattern in patterns:
            data = re.sub(pattern, "", data)
        return data
