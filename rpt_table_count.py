import pymysql

class TableCount:
    def __init__(self,params):
        self.params = params
        self.insert_data_base = self.params['insert_data_base']
        self.insert_table = self.params['insert_table']
        self.MYSQLCONFIG = {}
        self.params.pop('insert_data_base')
        self.params.pop('insert_table')
        self.MYSQLCONFIG.update(self.params)
        self.conn = pymysql.connect(**self.MYSQLCONFIG)
        self.cursor = self.conn.cursor()

    #执行sql  数据库commit 提交事务
    def execute_sql(self,sql):
        self.cursor.execute(sql)
        self.conn.commit()

    #创建统计的数据库(已存在则跳过) 创建统计的数据表(已存在删除)
    def create_data_base(self):
        create_sql = '''
CREATE DATABASE  If Not Exists `{}` Character Set UTF8;
USE `{}`;
DROP TABLE If Exists `{}`;
CREATE TABLE `{}`(
id INT(11) AUTO_INCREMENT COMMENT"主键id自增",
data_base VARCHAR(50) COMMENT "数据库",
table_name VARCHAR(50) COMMENT "表名称",
table_comment VARCHAR(100) COMMENT "表说明",
counts INT(11) COMMENT"数据量",
create_time DATETIME COMMENT "统计日期",
PRIMARY KEY(id),
KEY(create_time),
KEY(data_base),
KEY(table_name)
)ENGINE=INNODB DEFAULT CHARSET=utf8 COMMENT"各数据库各表数据量统计"
'''
        self.execute_sql(create_sql.format(self.insert_data_base,self.insert_data_base,self.insert_table,self.insert_table))
        print('数据库:{}--->创建成功\n统计表:{}--->创建成功'.format(self.insert_data_base,self.insert_table))
    #查询所有的数据库 并将安装mysql时候自带的库 在列表中删除
    def query_data_bases(self):
        sql = 'show databases'
        self.cursor.execute(sql)
        datas = self.cursor.fetchall()
        data_bases = [x[0] for x in datas]
        index_1 = data_bases.index('information_schema')
        data_bases.pop(index_1)
        index_2 = data_bases.index('performance_schema')
        data_bases.pop(index_2)
        index_3 = data_bases.index('mysql')
        data_bases.pop(index_3)
        return data_bases

    #查询表的信息 所在数据库 表名称 表注释 方便写入统计数据表中
    def query_table_infos(self,data_bases):
        query_table_sql =  '''
        select TABLE_SCHEMA,TABLE_NAME,TABLE_COMMENT
        FROM `information_schema`.TABLES
        where TABLE_SCHEMA = '{}' and TABLE_NAME <> '{}'
        '''
        for data_base in data_bases:
            sql = query_table_sql.format(data_base,self.insert_table)
            self.cursor.execute(sql)
            table_infos = self.cursor.fetchall()
            for data_base,table_name,table_comment in table_infos:
                item = {}
                item['data_base'] = data_base
                item['table_name'] = table_name
                item['table_comment'] = table_comment
                yield item

    #生成每一张表的写入统计报表的sql
    def make_sqls(self,items):
        for item in items:
            data_base = item['data_base']
            table_name = item['table_name']
            table_comment = item['table_comment']
            base_sql = '''
insert into `{}`.`{}`(
data_base,
table_name,
table_comment,
counts,
create_time
)
SELECT '{}' AS data_base,
'{}' AS table_name,
'{}' AS table_comment,
COUNT(*) AS counts,
SYSDATE() AS create_time
FROM `{}`.`{}`;
'''
            sql = base_sql.format(self.insert_data_base,self.insert_table,data_base,table_name,table_comment,data_base,table_name)
            print(sql)
            self.execute_sql(sql)
        return '执行成功'
    #调度 启动
    def run(self):
        data_bases = self.query_data_bases()
        items = self.query_table_infos(data_bases)
        info = self.make_sqls(items)
        return info

    def __str__(self):
        return self.insert_table


if __name__ == '__main__':
    params = {
        'insert_data_base': '报表要写入的数据库名',
        'insert_table': '写入的数据表(指定会自动创建 存在先删除再创建)',
        'host': '数据库ip',
        'user': '数据库用户',
        'password': '密码',
        'charset': 'utf8'
    }

    tbcount = TableCount(params)
    tbcount.create_data_base()
    info = tbcount.run()
    print(info)

