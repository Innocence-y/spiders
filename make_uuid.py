import pymysql
import uuid
import redis

'''
问题
1:使用 Python 如何生成 200 个激活码（或者优惠券）？
2:保存到mysql数据库
3:保存到redis数据库
'''

def get_id(num):
    list_id = []
    for i in range(num):
        id = str(uuid.uuid1()).replace('-','')
        list_id.append(id)
    return list_id

def insert_mysql(list_id):
    try:
        conn = pymysql.connect(host='localhost',user='root',passwd='密码',port=3306)
        cur = conn.cursor()
        conn.select_db('local_db')
        cur.execute('create table if not exists Activation_code(id int ,uuid varchar(50))')
        for index,value in enumerate(list_id):
            cur.execute('insert into Activation_code values(%s,%s)',(index+1,value))
        conn.commit()
        cur.close()
        conn.close()
    except pymysql.Error as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
def insert_redis(list_id):
    host = '127.0.0.1'
    port = 6379
    r = redis.StrictRedis(host=host, port=port)
    for index,value in enumerate(list_id):
        key = index +1
        print(key)
        r.set(key, value)


if __name__ == '__main__':
    list_id = get_id(200)
    insert_mysql(list_id)
    insert_redis(list_id)

