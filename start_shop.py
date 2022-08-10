import time
import requests
from pyquery import PyQuery as pq
import pandas as pd
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"

headers = {
    'User-Agent': ua,
    'Cookie':'cy=8; cye=chengdu; s_ViewType=10; _hc.v=5161ffe9-3584-4427-bfbc-0bc186b6f810.1616820694; dplet=e75afa67846dd4804c9426f6605a2e01; dper=6a4878f939db07b6b8574d5f77c73db24e4bfdaaa984f8742aa2ae1568564f0613168fb14ce64e1513358b66eb2cf1b918c910440932b3084bea4bb8ed6d21a14fe0ed6b85254e7e5895acefea0e617b40eeb3c89cc781ba46ac6f3a63d63a66; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_9922693141; ctu=fa1d87855e0de14722acf47734f18d7dd02a96188da4f910cbca8f91f5678817'
     }
def restaurant(url):
    # Get static source code of webpage
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except Exception:
        return None
name=[]
restid= []
star = []
recommend = []
url = []
image = []
def getImageUrl(htm):
    li=[]
    li = htm.split('%')
    return li[0]
def getRestId(htm2):
    id = []
    id = htm2.split('shop/')
    return id[1]
def info_restaurant(html):
    # Get the html
    doc = pq(html)
    for i in range(1,16):
        #Get restaurant name
        shop_name = doc('#shop-all-list > ul > li:nth-child('+str(i)+') > div.txt > div.tit > a:nth-child(1) > h4').text()
        if shop_name == '':
            break
        name.append(shop_name)
        #Get restaurant link
        url.append(doc('#shop-all-list > ul > li:nth-child('+str(i)+') > div.pic > a').attr('href'))
        restid.append(doc('#shop-all-list > ul > li:nth-child('+str(i)+') > div.pic > a').attr('data-shopid'))
        try:
            star.append(doc('#shop-all-list > ul > li:nth-child('+str(i)+') > div.txt > div.comment > div.nebula_star >div:nth-child(2)').text())
        except:
            star.append("")
        #Get Restaurant image
        try:
            image.append(getImageUrl(doc('#shop-all-list > ul > li:nth-child('+str(i)+') > div.pic > a > img').attr('src')))
        except:
            image.append("")
        #Get Recommended dishes
        try:
            recommend.append(doc('#shop-all-list > ul > li:nth-child('+str(i)+') > div.txt > div.recommend > a:nth-child(2)').text()+str(',')+\
                            doc('#shop-all-list > ul > li:nth-child('+str(i)+') > div.txt > div.recommend > a:nth-child(3)').text()+str(',')+\
                            doc('#shop-all-list > ul > li:nth-child('+str(i)+') > div.txt > div.recommend > a:nth-child(4)').text())
        except:
            recommend.append("")
for i in range(1,20):#51
    print('Getting Cafe cuisine based Restaurant information on page {}'.format(i))
    cantonese_url = 'http://www.dianping.com/chengdu/ch10/g132p'+str(i)+'?aid=93195650%2C68215270%2C22353218%2C98432390%2C107724883&cpt=93195650%2C68215270%2C22353218%2C98432390%2C107724883&tc=3'
    html = restaurant(cantonese_url)
    print(html)
    info_restaurant(html)
    print ('Successfully obtained page {}'.format(i))
    time.sleep(12)
shop = {'restid': restid, 'name': name,'star': star,'recommend': recommend,'url': url, 'image':image}
shop = pd.DataFrame(shop, columns=['restid','name', 'star', 'recommend', 'url','image'])
shop.to_csv("shop_info_cafe.csv",encoding="utf_8_sig",index = False)