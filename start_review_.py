

from dianping import DianpingComment
import pandas as pd

COOKIES = 'navCtgScroll=0; navCtgScroll=0; cy=8; cye=chengdu; s_ViewType=10; _hc.v=7809d0cd-174c-924d-7018-6ab86f4d5349.1616819374; fspop=test; cityid=8; switchcityflashtoast=1; default_ab=index%3AA%3A3%7CshopList%3AC%3A5; _dp.ac.v=17362cae-a3b5-4cdd-bed7-ccac62373966; ctu=29914abc252cf429c51de8596c7c639998ce9cfb64595a94d10ad85ee507c233; dplet=7b62a9298613ed5d8ffd039a076fb9cb; dper=6a4878f939db07b6b8574d5f77c73db206fa41823d1ecbedfbda7b606c2231b3aa78cdc13891e5650ca042c8dd62ff1db35b2b825dba8558f00e2fa2f02ed32fb399b6c6a5e4bfdd33cf5bad9394018d646294b5286e4658f8c908424bca290c; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_9922693141'


class Customer(DianpingComment):

    def _data_pipeline(self, data):
        #print(data)
        with open('shop_review_cafe.txt','a+',encoding='utf-8')as f:
            f.write(str(data)+'\n')


if __name__ == "__main__":
    df = pd.read_csv('shop_info_cafe.csv')
    restids= df['restid']
    restids = restids[94:100]
    for restid in restids:
        print('Crawling Restaurant:' + restid)
        dianping = Customer(restid, cookies=COOKIES)
        dianping.run()
    
