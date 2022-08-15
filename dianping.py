import datetime
import random
import re
import time
import json

import requests
from lxml import etree


class DianpingComment:
    font_size = 14
    start_y = 23
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.61 Safari/537.36 Edg/90.0.818.36'
    def __init__(self, shop_id, cookies, delay=7):
        self.shop_id = shop_id
        self._delay = delay
        self.font_dict = {}
        self._cookies = self._format_cookies(cookies)
        self._css_headers = {
            'User-Agent': self.ua,
        }
        self._default_headers = {
            'Connection': 'keep-alive',
            'Host': 'www.dianping.com',
            'User-Agent': self.ua,
            'Cookie':'cy=8; cye=chengdu; s_ViewType=10; _hc.v=5161ffe9-3584-4427-bfbc-0bc186b6f810.1616820694; dplet=e75afa67846dd4804c9426f6605a2e01; dper=6a4878f939db07b6b8574d5f77c73db24e4bfdaaa984f8742aa2ae1568564f0613168fb14ce64e1513358b66eb2cf1b918c910440932b3084bea4bb8ed6d21a14fe0ed6b85254e7e5895acefea0e617b40eeb3c89cc781ba46ac6f3a63d63a66; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_9922693141; ctu=fa1d87855e0de14722acf47734f18d7dd02a96188da4f910cbca8f91f5678817'
            }
        self._cur_request_url = 'http://www.dianping.com/shop/{}/review_all/p1'.format(shop_id) + '?aid=93195650%2C68215270%2C22353218%2C98432390%2C107724883&cpt=93195650%2C68215270%2C22353218%2C98432390%2C107724883&tc=3'
        self._cur_request_css_url = 'http://www.dianping.com/shop/{}/'.format(shop_id)

    def _delay_func(self):
        delay_time = 12 #random.randint((self._delay - 2) * 10, (self._delay + 2) * 10) * 0.1
        print('Wait for :', delay_time)
        time.sleep(delay_time)

    def _format_cookies(self, cookies):
        cookies = {cookie.split('=')[0]: cookie.split('=')[1]
                   for cookie in cookies.replace(' ', '').split(';')}
        return cookies

    def _get_css_link(self, url):
        res = requests.get(self._cur_request_url, headers=self._default_headers)
        html = res.text
        #print('首页源码',html)
        re_info = re.search(r'href="//s3plus(.*?)"', html)
        css_link = "http://s3plus" + re_info.group(1)
        return css_link



    def _get_font_dict_by_offset(self, url):
        res = requests.get(url,timeout=60)
        html = res.text
        font_dict = {}
        y_list = re.findall(r'd="M0 (\d+?) ', html)
        if y_list:
            font_list = re.findall(r'<textPath .*?>(.*?)<', html)
            for i, string in enumerate(font_list):
                y_offset = self.start_y - int(y_list[i])

                sub_font_dict = {}
                for j, font in enumerate(string):
                    x_offset = -j * self.font_size
                    sub_font_dict[x_offset] = font

                font_dict[y_offset] = sub_font_dict

        else:
            font_list = re.findall(r'<text.*?y="(.*?)">(.*?)<', html)

            for y, string in font_list:
                y_offset = self.start_y - int(y)
                sub_font_dict = {}
                for j, font in enumerate(string):
                    x_offset = -j * self.font_size
                    sub_font_dict[x_offset] = font

                font_dict[y_offset] = sub_font_dict
       
        return font_dict

    def _get_font_dict(self, url):
        res = requests.get(url, headers=self._css_headers,cookies=self._cookies,timeout=60)
        html = res.text

        background_image_link = re.findall(r'background-image: url\((.*?)\);', html)
        assert background_image_link
        background_image_link = 'http:' + background_image_link[0]
        html = re.sub(r'span.*?\}', '', html)
        group_offset_list = re.findall(r'\.([a-zA-Z0-9]{5,6}).*?round:(.*?)px (.*?)px;', html)  
        font_dict_by_offset = self._get_font_dict_by_offset(background_image_link)  



        for class_name, x_offset, y_offset in group_offset_list:
            y_offset = y_offset.replace('.0', '')
            x_offset = x_offset.replace('.0', '')
            # print(y_offset,x_offset)
            if font_dict_by_offset.get(int(y_offset)):
                self.font_dict[class_name] = font_dict_by_offset[int(y_offset)][int(x_offset)]

        return self.font_dict

    def _data_pipeline(self, data):

    def _parse_comment_page(self, doc):
    
        for li in doc.xpath('//*[@class="reviews-items"]/ul/li'):
            #Get the reviewer name
            try:
                name = li.xpath('.//a[@class="name"]/text()')[0].strip('\n\r \t')
            except IndexError:
                name = 'unknown'
            #Get the rating
            try:
                star = li.xpath('.//span[contains(./@class, "sml-str")]/@class')[0]
                star = re.findall(r'sml-rank-stars sml-str(.*?) star', star)[0]
            except IndexError:
                star = 0
            #Get the date
            time = li.xpath('.//span[@class="time"]/text()')[0].strip('\n\r \t')
            #Get the review content
            comment = ''.join(li.xpath('.//div[@class="review-words Hide"]/text()')).strip('\n\r \t')
            if not comment:
                comment = ''.join(li.xpath('.//div[@class="review-words"]/text()')).strip('\n\r \t')

            data = {
                "restid": self.shop_id,
                "name": name,
                "comment": comment,
                "star": star,
                "time": time,
            }
            self._data_pipeline(data)

    def _get_conment_page(self): 
        i = 3 #number of pages
        while self._cur_request_url:
            self._delay_func()
            print('[{now_time}] {msg}'.format(now_time=datetime.datetime.now(), msg=self._cur_request_url))
            res = requests.get(self._cur_request_url, headers=self._default_headers, cookies=self._cookies)
            html = res.text
            class_set = set()
            for span in re.findall(r'<span class="([a-zA-Z0-9]{5,6})"></span>', html):
                class_set.add(span)
            for class_name in class_set:
                html = re.sub('<span class="%s"></span>' % class_name, self._font_dict[class_name], html)
            doc = etree.HTML(html)
            self._parse_comment_page(doc)
            i = i-1
            if i !=0:
                try:
                    self._default_headers['Referer'] = self._cur_request_url
                    next_page_url = 'http://www.dianping.com' + doc.xpath('.//a[@class="NextPage"]/@href')[0]
                except IndexError:
                    next_page_url = None
                self._cur_request_url = next_page_url
            else:
                self._cur_request_url = None
            
            

    def run(self):
        self._css_link = self._get_css_link(self._cur_request_url)
        self._font_dict = self._get_font_dict(self._css_link)
        self._get_conment_page()
