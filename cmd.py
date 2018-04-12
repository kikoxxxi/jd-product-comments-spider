from scrapy import cmdline
cmdline.execute("scrapy crawl product_comments_spider -o items.json".split())
