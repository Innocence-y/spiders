import json
import requests
from lxml import etree
import pymysql


class Ts_Kr(object):
    def __init__(self):
        self.base_url = 'http://36kr.com/api/post?column_id={}&b_id={}&per_page=100'
        self.start_url = 'http://36kr.com/api/post?column_id={}&per_page=1'
        self.req_urls = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',

        }
        #数据库配置
        self.MYSQL_CONFIG = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '密码',
            'db': 'local_db',
            'charset': 'utf8'
        }
        self.conn = pymysql.connect(**self.MYSQL_CONFIG)
        #api接口参数字典
        self.column_ids_dict = {'column_ids': [67, 23, 102, 185, 180, 70, 103],
                                'column_names': ['早期项目', '大公司', '创投新闻', 'AI is', '消费升级', '深氪', '技能Get']}
        self.column_dict = dict(zip(self.column_ids_dict['column_ids'], self.column_ids_dict['column_names']))
    #第一次请求解析出后续的请求url
    def parse_column(self):
        column_ids = self.column_ids_dict['column_ids']
        print(column_ids, self.column_dict)
        for column_id in column_ids:
            self.parse_first_req(column_id)

    def parse_first_req(self, column_id):
        first_url = self.start_url.format(column_id)
        print(first_url)
        html = requests.get(first_url).text
        items = json.loads(html)['data']['items']
        if items:
            last_b_id = items[-1]['id']
            full_url = self.base_url.format(column_id, last_b_id)
            print('解析导航栏:%s-->首页,id-->%s' % (self.column_dict[column_id], column_id))
            self.parse_json(full_url)
        else:
            pass
    #解析 http://36kr.com/api/post?column_id=23&b_id=5070043&per_page=100 数据网为100个item循环遍历
    def parse_json(self, full_url):
        print("解析组合url--->", full_url)
        self.req_urls.append(full_url)
        html = requests.get(full_url).text
        items = json.loads(html)['data']['items']
        if items:
            for item in items:
                parse_item = item
                parse_item['tag'] = self.column_dict[item['column_id']]
                parse_item['full_url'] = full_url
                self.insert_item(parse_item)
            last_b_id = items[-1]['id']
            column_id = items[-1]['column_id']
            next_req_url = self.base_url.format(column_id, last_b_id)
            print('下一次请求url-->', next_req_url)
            #递归
            self.parse_json(next_req_url)
        else:
            pass
    #入库
    def insert_item(self, item):
        full_url = item['full_url']
        column_id = item['column_id'] if 'column_id' in item.keys() else None
        tag = self.column_dict[column_id]
        b_id = item['id'] if 'id' in item.keys() else None
        article_url = 'http://36kr.com/p/{}.html'.format(b_id) if 'id' in item.keys() else None
        title = item['title'] if 'title' in item.keys() else None
        user_id = item['user_id'] if 'user_id' in item.keys() else None
        user_name = item['user']['name'] if 'user' in item.keys() and item['user']['name'] else None
        total_words = item['total_words'] if 'total_words' in item.keys() else None
        close_comment = item['close_comment'] if 'close_comment' in item.keys() else None
        favorite = item['counters']['favorite'] if 'counters' in item.keys() and item['counters']['favorite'] else None
        likes = item['counters']['like'] if 'counters' in item.keys() and item['counters']['like'] else None
        pv = item['counters']['pv'] if 'counters' in item.keys() and item['counters']['pv'] else None
        pv_app = item['counters']['pv_app'] if 'counters' in item.keys() and item['counters']['pv_app'] else None
        pv_mobile = item['counters']['pv_mobile'] if 'counters' in item.keys() and item['counters']['pv_mobile'] else None
        view_count = item['counters']['view_count']if 'counters' in item.keys() and item['counters']['view_count'] else None
        extraction_tags = item['extraction_tags'] if 'extraction_tags' in item.keys() else None
        summary = item['summary'] if 'summary' in item.keys() else None
        title_mobile = item['title_mobile'] if 'title_mobile' in item.keys() else None
        introduction = item['column']['introduction'] if 'column' in item.keys() and item['column']['introduction'] else None
        published_at = item['published_at'] if 'published_at' in item.keys() else None
        created_at = item['created_at'] if 'created_at' in item.keys() else None
        updated_at = item['updated_at'] if 'updated_at' in item.keys() else None
        related_company_id = item['related_company_id'] if 'related_company_id' in item.keys() else None
        related_company_type = item['related_company_type'] if 'related_company_type' in item.keys() else None
        related_company_name = item['related_company_name'] if 'related_company_name' in item.keys() else None
        args = (column_id,tag,b_id,article_url,title,user_id,user_name,total_words,close_comment,favorite,likes,pv,pv_app,pv_mobile,view_count,extraction_tags,summary,title_mobile,introduction,published_at,created_at,updated_at,related_company_id,related_company_type,related_company_name,full_url)
        values_format=",".join(['%s' for i in range(1,len(args)+1)])
        insert_sql = 'insert into 36kr (column_id,tag,b_id,article_url,title,user_id,user_name,total_words,close_comment,favorite,likes,pv,pv_app,pv_mobile,view_count,extraction_tags,summary,title_mobile,introduction,published_at,created_at,updated_at,related_company_id,related_company_type,related_company_name,full_url) values(%s)' % (values_format)
        cursor.execute(insert_sql,args)
        print(args)
        conn.commit()
if __name__ == '__main__':
    _36kr = Ts_Kr()
    conn = _36kr.conn
    cursor = conn.cursor()
    _36kr.parse_column()
    cursor.close()
    conn.close()
    print('共请求%s个URL' % (len(_36kr.req_urls)))

