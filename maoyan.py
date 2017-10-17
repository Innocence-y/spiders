"""
python版本:3.6
首先抓取猫眼电影标签:分类 地区 年代
根据标签的三种组合 得到电影url 也就知道了这部电影是什么题材 什么地区 什么年代的属性

"""


import requests
from lxml import etree


class MaoyanSpider(object):
    def __init__(self):
        self.start_url = 'http://maoyan.com/films'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cookie': '你的cookie',
            'Host': 'maoyan.com',
            'Referer': 'http://maoyan.com/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
        }

    # 解析猫眼电影 请求的url组合 分类 地区 年代
    def parse_urls(self):
        html = requests.get(self.start_url, headers=self.headers).text
        selector = etree.HTML(html)
        infos = selector.xpath('//div[@class="movies-channel"]/div[@class="tags-panel"]/ul[@class="tags-lines"]/li/ul[@class="tags"]/li[position()>1]')
        item = {}
        item['分类'] = []
        item['地区'] = []
        item['年代'] = []
        big_dic = {}
        for type_info in infos:
            href = type_info.xpath('a/@href')[0]
            text = type_info.xpath('a/text()')[0]
            dic = {href: text}
            big_dic[href] = text
            if 'cat' in href:
                type = '分类'
                item[type].append(dic)
            elif 'sourceId' in href:
                type = '地区'
                item[type].append(dic)
            else:
                type = '年代'
                item[type].append(dic)
        all_url = []
        cats = []
        for cat in item['分类']:
            cats.append(list(cat.keys())[0])
        areas = []
        for area in item['地区']:
            areas.append(list(area.keys())[0])
        years = []
        for year in item['年代']:
            years.append(list(year.keys())[0])
        for cat in cats:
            for area in areas:
                for year in years:
                    url = self.start_url + cat + '&' + area.lstrip('?') + '&' + year.lstrip('?')
                    tags = big_dic[cat] + "," + big_dic[area] + "," + big_dic[year]
                    all_url.append({'url': url, 'tags': tags})
        return all_url

    # 根据不同请求 解析出电影的url以及该电影的属性
    def parse_moive(self, item):
        html = requests.get(item['url'], headers=self.headers).text
        selector = etree.HTML(html)
        infos = selector.xpath('//div[@class="movies-list"]/dl[@class="movie-list"]//div[@class="channel-detail movie-item-title"]/a')
        if len(infos) > 0:
            for info in infos:
                movie_url = 'http://maoyan.com' + info.xpath('@href')[0]
                movie_name = info.xpath('text()')[0]
                print(movie_name, movie_url, item['tags'])
        else:
            pass


if __name__ == '__main__':
    maoyan = MaoyanSpider()
    all_urls = maoyan.parse_urls()
    for i in range(len(all_urls)):
        item = all_urls[i]
        print(i + 1, '------->', item['url'])
        maoyan.parse_moive(item)
