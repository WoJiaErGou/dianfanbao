import scrapy
from scrapy import Selector
import requests
from requests import Session,adapters
import re
import time
from bs4 import BeautifulSoup
from gm_dianfanbao.items import GmDianfanbaoItem

class DFB_spider(scrapy.Spider):
    name='gm_DFB'
    start_urls=['http://list.gome.com.cn/cat10000188.html?intcmp=sy-1000053151-2']
    def parse(self, response):
        #找出查询结果数量以及页码数量
        max_numbers=re.findall('共 <em id="searchTotalNumber">(.*?)</em> 个商品',response.text)[0]
        print(max_numbers)
        page_numbers=Selector(response).re(' totalPage   :(.*?),')[0]
        print(page_numbers)
        for i in range(1,int(page_numbers)+1):
            page_url='http://list.gome.com.cn/cat10000188-00-0-48-1-0-0-0-1-0-0-0-0-0-0-0-0-0.html?&page=%d' % i
            yield scrapy.Request(url=page_url,callback=self.product_page,dont_filter=True)
    def product_page(self,response):
        #商品集合页查询商品名称，店铺名称，商品详情页url
        for each in response.xpath(".//div[@class='item-tab-warp']"):
            p_Name=each.xpath(".//p[@class='item-name']/a/text()").extract()[0]
            # print(p_Name)
            product_urlm=each.xpath(".//p[@class='item-name']/a/@href").extract()[0]
            # print(product_urlm)
            product_url='http:'+product_urlm
            item=GmDianfanbaoItem(p_Name=p_Name,product_url=product_url)
            # 检测product_url是否符合标准，是否多http：///
            http_list = re.findall(r'http:/+', product_url)
            if len(http_list) > 1:
                url_n = 'http:' + product_url.split('http:')[-1]
                # print(url_n)
                request = scrapy.Request(url=url_n, callback=self.detail, meta={'item': item}, dont_filter=True)
                yield request
            else:
                # print(product_url)
                request = scrapy.Request(url=product_url, callback=self.detail, meta={'item': item},dont_filter=True)
                yield request
    def detail(self,response):
        item=response.meta['item']
        product_url=item['product_url']
        # text=product_text
        '''检测到网页长度不足证明网页内容不全，重新获取'''
        if len(response.text)<65000:
            yield scrapy.Request(url=product_url,callback=self.detail,meta=response.meta,dont_filter=True)
            return None
        # 商品ID
        try:
            ProductID = Selector(response).re('prdId:"(.*?)"')[0]
        except:
            try:
                ProductID = re.findall('prdId:"(.*?)"', response.text)[0]
            except:
                try:
                    ProductID = re.findall('prdId:"(.*?)"', response.text)[0]
                except:
                    ProductID = response.url.split('/')[-1].split('-')[0]
        # 好评，差评等信息采集
        comment_url = 'http://ss.gome.com.cn/item/v1/prdevajsonp/appraiseNew/%s/1/all/0/10/flag/appraise' % ProductID
        mark_url = 'http://ss.gome.com.cn/item/v1/prdevajsonp/productEvaComm/%s/flag/appraise/totleMarks?callback=totleMarks' % ProductID
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        request_retry=requests.adapters.HTTPAdapter(max_retries=3)
        with Session() as gome:
            #建立会话对象
            gome.mount('http://',request_retry)
            gome.mount('https://',request_retry)
            gome.headers=headers
            comment_text=gome.get(url=comment_url).text
            time.sleep(0.3)
            mark_text=gome.get(url=mark_url).text
        #店铺名称
        try:
            shop_name=response.xpath(".//div[@class='zy-stores shops-name']/a[@class='name']/text()").extract()[0]
        except:
            try:
                shop_name=response.xpath(".//h2[@id='store_live800_wrap']/a[@class='name']/text()").extract()[0]
            except:
                try:
                    shop_name=response.xpath(".//div[@class='zy-stores shops-name']/span[@class='identify']/text()").extract()[0]
                except:
                    shop_name=None
        #价格类代码重写
        try:
            Price = re.findall('price:"(.*?)"', response.text)
            gomeprice = re.findall('gomePrice:"(.*?)"', response.text)
            groupprice = re.findall('groupPrice:"(.*?)"', response.text)
            oldprice = re.findall('<span id="listPrice">(.*?)</span>', response.text)
            if Price:
                if Price[0]=='0':
                    price=gomeprice[0]
                    PreferentialPrice=gomeprice[0]
                else:
                    if float(Price[0])<float(gomeprice[0]):
                        price=gomeprice[0]
                        PreferentialPrice=Price[0]
                    else:
                        price=Price[0]
                        PreferentialPrice=gomeprice[0]
            else:
                if float(oldprice[0])<float(groupprice[0]):
                    price=groupprice[0]
                    PreferentialPrice=oldprice[0]
                else:
                    price=oldprice[0]
                    PreferentialPrice=groupprice[0]
            if float(price)< float(PreferentialPrice):
                print('错误！！！')
        except:
            price=None
            PreferentialPrice=None

        #品牌
        try:
            brand=Selector(response).re('品牌：(.*?)</div>')[0]
        except:
            try:
                brand=re.findall('品牌：(.*?)</div>',response.text)[0]
            except:
                brand=None
        if brand:
            if re.findall(r'（.*?）', brand):
                re_com = re.compile('（.*?）')
                brand = brand[:0] + re.sub(re_com, '', brand)
        if brand:
            if re.findall(r'(.*?)', brand):
                re_cn = re.compile('\(.*?\)')
                brand = brand[:0] + re.sub(re_cn, '', brand)
        #品牌型号
        try:
            X_name=Selector(response).re('型号：(.*?)</div>')[0]
        except:
            try:
                X_name=re.findall('型号：(.*?)</div>',response.text)[0]
            except:
                try:
                    X_name=Selector(response).re('型号</span><span>(.*?)</span>')[0]
                except:
                    try:
                        X_name=re.findall('型号</span><span>(.*?)</span>',response.text)[0]
                    except:
                        X_name=None
        if X_name:
            if brand:
                if brand in X_name:
                    pass
                else:
                    X_name = brand + X_name[:]
        # 颜色
        try:
            color = Selector(response).re('颜色</span><span>(.*?)</span>')[0]
        except:
            try:
                color = re.findall('颜色</span><span>(.*?)</span>', response.text)[0]
            except:
                color = None
        #功能，加热方式，控制方式，预约方式
        try:
            jiare=Selector(response).re('加热方式：(.*?)</div>')[0]
        except:
            try:
                jiare=Selector(response).re('加热方式</span><span>(.*?)</span>')[0]
            except:
                try:
                    jiare=re.findall('加热方式：(.*?)</div>',response.text)[0]
                except:
                    try:
                        jiare=re.findall('加热方式</span><span>(.*?)</span>',response.text)[0]
                    except:
                        jiare=None
        try:
            kongzhi=Selector(response).re('控制方式：(.*?)</div>')[0]
        except:
            try:
                kongzhi=Selector(response).re('控制方式</span><span>(.*?)</span>')[0]
            except:
                try:
                    kongzhi=re.findall('控制方式：(.*?)</div>',response.text)[0]
                except:
                    try:
                        kongzhi=re.findall('控制方式</span><span>(.*?)</span>',response.text)[0]
                    except:
                        kongzhi=None
        try:
            yuyue=Selector(response).re('预约方式：(.*?)</div>')[0]
        except:
            try:
                yuyue=Selector(response).re('预约方式</span><span>(.*?)</span>')[0]
            except:
                try:
                    yuyue=re.findall('预约方式：(.*?)</div>',response.text)[0]
                except:
                    try:
                        yuyue=re.findall('预约方式</span><span>(.*?)</span>',response.text)[0]
                    except:
                        yuyue=None
        if jiare or kongzhi or yuyue:
            X_type=''
            if jiare:
                X_type=X_type[:]+jiare+' '
            if kongzhi:
                X_type=X_type[:]+kongzhi+' '
            if yuyue:
                X_type=X_type[:]+yuyue
            if len(X_type) < 1:
                X_type=None
        else:
            X_type=None
        #容量
        try:
            capacity=Selector(response).re('容量：(.*?)</div>')[0]
        except:
            try:
                capacity=Selector(response).re('容量</span><span>(.*?)</span>')[0]
            except:
                try:
                    capacity=re.findall('容量：(.*?)</div>',response.text)[0]
                except:
                    try:
                        capacity=re.findall('容量</span><span>(.*?)</span>',response.text)[0]
                    except:
                        capacity=None
        #####核心参数，特别处理部分
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            parameter = []
            div_item = soup.find_all('div', class_='param-item')
            # print(div_item)
            for each in div_item:
                li_list = each.find_all('li')
                for each in li_list:
                    li_text = re.sub(r'\n', '', each.text)
                    parameter.append(li_text)
            if len(parameter) < 1:
                print(1 / 0)
        except:
            try:
                parameter = []
                div_item = soup.find('div', class_='guigecanshu_wrap')
                div_canshu = div_item.find_all('div', class_='guigecanshu')
                for each in div_canshu:
                    parameter.append(each.text)
                if len(parameter) < 1:
                    print(1 / 0)
            except:  # 针对真划算页面的type参数分析
                try:
                    parameter = []
                    table = soup.find('table', attrs={'class': 'grd-specbox'})
                    tr_list = table.find_all('tr')
                    for each in tr_list:
                        if each.find('td'):
                            td = each.find_all('td')
                            if td:
                                td1 = re.sub(r'\n', '', td[0].text)
                                td2 = re.sub(r'\n', '', td[1].text)
                                parameter.append(td1 + ':' + td2)
                                # print(td1 + ':' + td2)
                    print(parameter)
                    if len(parameter) < 1:
                        print(1 / 0)
                except:
                    parameter = None
        # 将核心参数转化为字符串形式
        try:
            if parameter == None:
                type = None
            else:
                type = '"'
                for i in range(len(parameter)):
                    type = type[:] + parameter[i]
                    if i < len(parameter) - 1:
                        type = type[:] + ' '
                    if i == len(parameter) - 1:
                        type = type[:] + '"'
        except:
            type = None
        if type:
            if brand==None:
                try:
                    brand=re.findall('品牌:(.*?) ',type)[0]
                except:
                    brand=None
            if brand:
                if re.findall(r'（.*?）', brand):
                    re_com = re.compile('（.*?）')
                    brand = brand[:0] + re.sub(re_com, '', brand)
            if brand:
                if re.findall(r'(.*?)', brand):
                    re_cn = re.compile('\(.*?\)')
                    brand = brand[:0] + re.sub(re_cn, '', brand)
            if X_name==None:
                try:
                    X_name=re.findall('型号:(.*?) ',type)[0]
                except:
                    X_name=None
            if X_name:
                if brand:
                    if brand in X_name:
                        pass
                    else:
                        X_name = brand + X_name[:]
            if color==None:
                try:
                    color=re.findall('颜色:(.*?) ',type)[0]
                except:
                    color=None
            '''
            以下为功能部分获取
            '''
            if X_type==None:
                try:
                    jiare=re.findall('加热方式:(.*?) ',type)[0]
                except:
                    jiare=None
                try:
                    kongzhi=re.findall('控制方式:(.*?) ',type)[0]
                except:
                    kongzhi=None
                try:
                    yuyue=re.findall('预约方式:(.*?) ',type)[0]
                except:
                    yuyue=None
                if jiare or kongzhi or yuyue:
                    X_type = ''
                    if jiare:
                        X_type = X_type[:] + jiare + ' '
                    if kongzhi:
                        X_type = X_type[:] + kongzhi + ' '
                    if yuyue:
                        X_type = X_type[:] + yuyue
                    if len(X_type) < 1:
                        X_type = None
                else:
                    X_type = None
            '''
            容量
            '''
            if capacity==None:
                try:
                    capacity=re.findall('容量:(.*?) ',type)[0]
                except:
                    capacity=None
        # 访问comment_url
        try:
            # 好评
            GoodCount = re.findall('"good":(.*?),', comment_text)[0]
        except:
            GoodCount = None
            # 中评
        try:
            GeneralCount = re.findall('"mid":(.*?),', comment_text)[0]
        except:
            GeneralCount = None
            # 差评
        try:
            PoorCount = re.findall('"bad":(.*?),', comment_text)[0]
        except:
            PoorCount = None
            # 总评
        try:
            CommentCount = re.findall('"totalCount":(.*?),', comment_text)[0]
        except:
            CommentCount = None
        # 访问评论关键字
        # 好评度
        try:
            GoodRateShow = re.findall(r'"goodCommentPercent":(\d+)', mark_text)[0]
        except:
            try:
                GoodRateShow = re.findall(r'"good":(\d+),', mark_text)[0]
            except:
                GoodRateShow = None
        try:
            keyword = '"'
            word_list = re.findall('"recocontent":"(.*?)"', mark_text)
            for each in word_list:
                if '?' in each:
                    word_list.remove(each)
            if word_list:
                for every in word_list:
                    keyword = keyword[:] + every
                    if every != word_list[-1]:
                        keyword = keyword[:] + ' '
                    if every == word_list[-1]:
                        keyword = keyword[:] + '"'
            if len(keyword) <= 1:
                print(1 / 0)
        except:
            keyword = None
        source='国美'
        if type==None and brand==None and X_name==None:
            print('一条数据被过滤！')
            yield None
        else:
            item['ProductID']=ProductID
            item['X_name'] = X_name
            item['type'] = type
            item['X_type'] = X_type
            item['price'] = price
            item['PreferentialPrice'] = PreferentialPrice
            item['brand'] = brand
            item['keyword'] = keyword
            item['PoorCount'] = PoorCount
            item['CommentCount'] = CommentCount
            item['GoodCount'] = GoodCount
            item['GeneralCount'] = GeneralCount
            item['GoodRateShow'] = GoodRateShow
            item['shop_name'] = shop_name
            item['capacity'] = capacity
            item['color'] = color
            item['source'] = source
            yield item