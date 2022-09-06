import requests
from requests.auth import HTTPBasicAuth
from lxml import etree
import os
import time
from datetime import datetime
import argparse


def replaceStr(s=''):
    return s.replace(' ', '').replace(',', '')

def mkdir(path):
    path=path.strip()
    path=path.rstrip('\\')
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path) 
        return True
    else:
        return False



cacheDir = './cache/'
mkdir(cacheDir)
cfile = cacheDir + 'lastTime.txt'
tformat = '%Y-%m-%d %H:%M:%S'

def cacheTime():
    try:
        now_str = datetime.now().strftime(tformat)
        with open(cfile, 'w') as f:
            f.write(now_str)
            f.close()
            print('cacheTime -> '+now_str)
    except IOError:
        print('cache file isNotExists')


def start(token, sendkey, ss):
    flag = False
    print('ss is '+ str(ss))
    url = 'https://tieba.baidu.com/f?kw=%E6%8B%BC%E5%A4%9A%E5%A4%9A%E9%BB%91%E5%8D%A1&ie=utf-8&pn=0'
    response = requests.get(url, timeout=(10, 10))
    selector = etree.HTML(response.text)
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d ')
    
    rs = []
    
    for i in selector.xpath('//*[@id="thread_list"]/li'):
        flag = True #读到数据视为成功
        ttexts = i.xpath('div/div[2]/div[1]/div[1]/a/text()')
        if len(ttexts) < 1:
            continue
        title = ':    ' + ttexts[0]
        bodys = i.xpath('div/div[2]/div[2]/div[1]/div/text()')
        if len(bodys) > 0 and len(replaceStr(bodys[0])) > 0:
            title = title + bodys[0]
        if title.find("五级") == -1 and title.find("5级") == -1 and title.find("六级") == -1 and title.find("6级") == -1:
            continue    
        time = replaceStr(i.xpath('div/div[2]/div[1]/div[2]/span[2]/text()')[0])
        if time.upper().find(":") == -1:
            continue
        dt_time = datetime.strptime(now_str + time, '%Y-%m-%d %H:%M')
        if (now - dt_time).seconds > ss:
            continue
        print(title, '   ----------   ', dt_time)
        rs.append(time+title)

    # 推送消息
    if len(rs) > 0:
        sp = '%0D%0A' #推送的换行符
        url = 'https://push.100180.xyz/wecomchan?sendkey=' + sendkey + '&msg_type=text&msg=pdd-hk ['+str(ss)+'s]  ' + now.strftime(tformat) + sp + sp
        msg = sp.join(rs)
        resp = requests.get(url + msg, timeout=(10, 10), auth=HTTPBasicAuth("admin", token), verify=False)
        if resp.status_code != 200 and resp.status_code != 201:  #推送失败视为整体失败，下次执行时任然可以拉取
            print('letserver push error -> ' + str(resp.status_code))
            flag = False

    if flag == True:
        cacheTime()


def getSsBycacheLastTime(ss):
    lastTimeStr = ''
    try:
        with open(cfile, 'r') as f:
            lastTimeStr = f.read()
    except IOError:
        print('cache file isNotExists')
    if len(lastTimeStr) < 1:
        return ss
    
    print('last tims is -> ' + lastTimeStr)
    lastTime = datetime.strptime(lastTimeStr, tformat)
    s = (datetime.now() - lastTime).seconds
    if s > ss:
        return s
    return ss



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", type=str, required=True)
    parser.add_argument("-k", type=str, required=True)
    parser.add_argument("-s", type=int, required=False, default=3600)
    args = parser.parse_args()
    # start(args.t, args.k, getSsBycacheLastTime(args.s) + 10)
    try:
        start(args.t, args.k, getSsBycacheLastTime(args.s) + 10)
        print('Finished')
    except:
        print('error')
