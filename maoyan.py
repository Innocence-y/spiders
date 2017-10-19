import os
import time
import requests
from lxml import etree
import pymysql


class MaoyanSpider(object):
    def __init__(self):
        self.start_url = "http://maoyan.com/films?offset={}"
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cookie': 'uuid=1A6E888B4A4B29B16FBA1299108DBE9C82758EE1DAA259161877DC413DAC7F2F; __mta=156086788.1508235018639.1508235469720.1508304232716.7; _lxsdk_s=ea22e2d284e036a176f9ec5be187%7C%7C6',
            'Host': 'maoyan.com',
            'Referer': 'http://maoyan.com/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
        }
        self.moive_list = []
        self.MYSQL_CONFIG = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'admin2016',
            'db': 'maoyan',
            'charset': 'utf8'
        }
        self.conn = pymysql.connect(**self.MYSQL_CONFIG)

    def all_req_url(self):
        all_req_url = []
        for i in range(9):
            offset = str(i * 30)
            req_url = self.start_url.format(offset)
            all_req_url.append(req_url)
        return all_req_url

    # 根据不同请求 解析出电影的url以及该电影的属性
    def parse_moive(self, url):
        html = requests.get(url, headers=self.headers).text
        selector = etree.HTML(html)
        infos = selector.xpath('//div[@class="movies-list"]/dl[@class="movie-list"]//div[@class="channel-detail movie-item-title"]/a')
        if len(infos) > 0:
            for info in infos:
                movie_url = 'http://maoyan.com' + info.xpath('@href')[0]
                movie_name = info.xpath('text()')[0]
                print(movie_name, movie_url)
                moive_item = {}
                moive_item['movie_name'] = movie_name
                moive_item['movie_url'] = movie_url
                moive_item['req_url'] = url
                self.moive_detail(moive_item)
        time.sleep(5)

    def moive_detail(self, moive_item):
        item = moive_item
        html = requests.get(moive_item['movie_url'], headers=self.headers).text
        selector = etree.HTML(html)
        try:
            eot_url = 'http://' + selector.xpath('//style/text()')[0].split(';')[1].strip().split('//')[1].replace("')",'')
            item['eot_url'] = eot_url
            # 解析字体 找到映射字典
            eot_dict = self.eot_to_dict(item)
            print("===解析eot===", eot_dict)
            # 想看数 票房
            want_see_nums_span = selector.xpath('//div[@class="movie-stats-container"]//div[@class="movie-index-content score normal-score"]//span[@class="stonefont"]/text()')
            if want_see_nums_span:
                try:
                    want_see_nums = "".join([eot_dict[x.encode('raw_unicode_escape').decode()[2::]] for x in want_see_nums_span[0]])
                except:
                    want_see_nums = "0"
            else:
                want_see_nums = '0'
            piaofang_span = selector.xpath('//div[@class="movie-stats-container"]//div[@class="movie-index-content box"]//span[@class="stonefont"]/text()')
            if piaofang_span:
                try:
                    piaofang = "".join([eot_dict[x.encode('raw_unicode_escape').decode()[2::]] for x in piaofang_span[0]])
                except:
                    piaofang = "0"
            else:
                piaofang = '0'
        except:
            print('eot文件异常',moive_item['movie_url'])
            want_see_nums = "0"
            piaofang = "0"
        ename_div = selector.xpath('//div[@class="ename ellipsis"]/text()')
        ename = ename_div[0] if len(ename_div) > 0 else '无别名'
        types = selector.xpath('//div[@class="movie-brief-container"]/ul/li/text()')
        infos = ";".join(['/'.join([y.strip() for y in x.strip().replace('\n', '').split('/')]) for x in types])
        movie_desc_span = selector.xpath('//span[@class="dra"]/text()')
        movie_desc = movie_desc_span[0] if len(movie_desc_span) > 0 else "无简介"
        celebritys_div = selector.xpath('//div[@class ="celebrity-container"]/div[@class="celebrity-group"][1]//div[@class="info"]/a/text()')
        celebritys = ';'.join([x.strip().replace('\n', '') for x in celebritys_div])
        actors_div = selector.xpath('//div[@class ="celebrity-container"]/div[@class="celebrity-group"][position()>1]//div[@class="info"]/a/text()')
        actors = ';'.join([x.strip().replace('\n', '') for x in actors_div])
        item['ename'] = ename
        item['movie_desc'] = movie_desc
        item['infos'] = infos
        item['celebritys'] = celebritys
        item['actors'] = actors
        item['want_see_nums'] = want_see_nums
        item['piaofang'] = piaofang
        print(piaofang)
        time.sleep(5)
        self.insert_moive(item)

    def has_next_tag(self, f):
        if f.read(1):
            f.seek(-1, 1)
            return True
        else:
            return False

    def eot_to_dict(self, item):
        dic = []
        eot_url = item['eot_url']
        eot_content = requests.get(eot_url).content
        file_name = '%s.eot' % item['movie_name']
        with open(file_name, 'wb') as eot:
            eot.write(eot_content)
        with open(file_name, 'rb') as f:
            while self.has_next_tag(f):
                f_type = f.read(1)
                if f_type == b'\x07' and f.read(1) == b'u':
                    f.seek(2, 1)
                    dic.append(((f.read(4).decode()).lower()))
        num = [str(i) for i in range(10)]
        item = dict(zip(dic, num))
        os.remove(file_name)
        return item
    def truncate_movie(self):
        truncate_sql='truncate table movie'
        cursor.execute(truncate_sql)
        conn.commit()


    def insert_moive(self, item):
        insert_sql = 'insert into movie (movie_url,movie_name,ename,want_see_nums,piaofang,movie_desc,infos,celebritys,actors,req_url) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(insert_sql, (
        item['movie_url'], item['movie_name'], item['ename'], item['want_see_nums'], item['piaofang'],item['movie_desc'], item['infos'],
        item['celebritys'], item['actors'], item['req_url']))
        print('插入成功')
        conn.commit()


if __name__ == '__main__':
    maoyan = MaoyanSpider()
    # moive_item = {'movie_url': 'http://maoyan.com/films/1204608', 'movie_name': '时间'}
    # print(moive_item['movie_url'])
    # maoyan.moive_detail(moive_item)
    conn = maoyan.conn
    cursor = conn.cursor()
    all_urls = maoyan.all_req_url()
    maoyan.truncate_movie()
    for url in all_urls:
        maoyan.parse_moive(url)
    cursor.close()
    conn.close()
