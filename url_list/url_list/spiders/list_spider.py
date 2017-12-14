import scrapy
from scrapy import Selector
import requests
from requests import Session,adapters
import re
import time
from bs4 import BeautifulSoup
from url_list.items import UrlListItem
class DFB_spider(scrapy.Spider):
    name='url_spi'
    # start_urls=['http://list.gome.com.cn/cat10000188.html?intcmp=sy-1000053151-2']
    start_urls = ['http://list.gome.com.cn/cat10000188.html?&page=29']
    def parse(self, response):
        #找出查询结果数量以及页码数量
        max_numbers=re.findall('共 <em id="searchTotalNumber">(.*?)</em> 个商品',response.text)[0]
        print(max_numbers)
        page_numbers=Selector(response).re(' totalPage   :(.*?),')[0]
        print(page_numbers)
        for each in response.xpath(".//div[@class='item-tab-warp']"):
            pageid=29
            url_m=each.xpath(".//p[@class='item-name']/a/@href").extract()[0]
            p_Name=each.xpath(".//p[@class='item-name']/a/text()").extract()
            print(p_Name)
            url="http:"+url_m
            item=UrlListItem(url=url,pageid=pageid,p_Name=p_Name)
            print(url)
            yield item
        # for i in range(1,int(page_numbers)+1):
        #     page_url='http://list.gome.com.cn/cat10000188-00-0-48-1-0-0-0-1-0-0-0-0-0-0-0-0-0.html?&page=%d' % i
        #     pageid=i
        #     yield scrapy.Request(url=page_url,callback=self.product_page,meta={'pageid':pageid})
    def product_page(self,response):
        #商品集合页查询商品名称，店铺名称，商品详情页url
        pageid=response.meta['pageid']
        with open('response_%s.txt' % pageid,'w',encoding='utf-8') as file:
            file.write(response.text)
        for each in response.xpath(".//div[@class='item-tab-warp']"):
            url_m=each.xpath(".//p[@class='item-name']/a/@href").extract()[0]
            p_Name=each.xpath(".//p[@class='item-name']/a/text()").extract()
            print(p_Name)
            url="http:"+url_m
            item=UrlListItem(url=url,pageid=pageid,p_Name=p_Name)
            print(url)
            yield item