# -*- coding: utf-8 -*-

# Scrapy settings for url_list project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'url_list'

SPIDER_MODULES = ['url_list.spiders']
NEWSPIDER_MODULE = 'url_list.spiders'
DOWNLOAD_DELAY = 5

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'url_list (+http://www.yourdomain.com)'

# Obey robots.txt rules
# USER_AGENT='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
DEFAULT_REQUEST_HEADERS={
    'Host':'list.gome.com.cn',
    'Referer':'http://list.gome.com.cn/cat10000188-00-0-48-1-0-0-0-1-0-0-0-10-0-0-0-0-0.html?intcmp=list-9000000600-11',
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
}
ROBOTSTXT_OBEY = False
AUTOTHROTTLE_ENABLED = True
RETRY_ENABLED=True
RETRY_TIMES=5
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware':False,
    # 'gm_dianfanbao.middlewares.GM_user':400,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware':True

}
ITEM_PIPELINES = {
   # 'sunings.pipelines.SuningsPipeline': 300,
    'url_list.pipelines.CSVPipeline':200
}
FIELDS_TO_EXPORT=[
    'url',
    'pageid',
    'p_Name'
]
