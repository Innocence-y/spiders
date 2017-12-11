import requests
from lxml import etree

class SoybaseSpider:
    start_url = 'http://www.soybase.org/search/qtllist_by_symbol.php/'
    base_url = 'https://www.soybase.org/'


    def parse(self):
        html = requests.get(self.start_url).text
        selector = etree.HTML(html)
        infos = selector.xpath('//td/a')
        for info in infos:
            item = {}
            item['first_url'] = self.base_url + info.xpath('@href')[0]
            item['first_name'] = info.xpath('text()')[0]
            item['response'] = requests.get(item['first_url']).text
            yield item

    def second_site(self,items):
        for item in items:
            item2 = {}
            html = item['response']
            selector = etree.HTML(html)
            second_url = self.base_url + selector.xpath('//table[@id="beantable"]/tr[2]/th[3]/a/@href')[0]
            item2['first_url'] = item['first_url']
            item2['first_name'] = item['first_name']
            item2['second_url'] = second_url
            item2['second_res'] = requests.get(second_url).text
            yield item2

    def third_site(self,items2):
        for item2 in items2:
            html = item2['second_res']
            selector = etree.HTML(html)
            tr_infos = selector.xpath('//tr[position()>1]')
            for tr in tr_infos:
                item3 = {}
                item3['first_url'] = item2['first_url']
                item3['first_name'] = item2['first_name']
                item3['second_url'] = item2['second_url']
                item3['QTL_url'] = self.base_url+tr.xpath('td[1]/a/@href')[0]
                item3['QTL_name'] = tr.xpath('td[1]/a/text()')[0]
                yield item3

    def parse_item(self,items):
        for item in items:
            print(item)



if __name__ == '__main__':
    soyspider = SoybaseSpider()
    items = soyspider.parse()
    items2 = soyspider.second_site(items)
    item3 = soyspider.third_site(items2)
    soyspider.parse_item(item3)







