import requests
from requests.auth import HTTPBasicAuth
from lxml import etree
import os
import time
from datetime import datetime
import argparse
import json
import re


def strToFloat(txt):
    txtLs = list(txt)
    rs = ""
    for c in txtLs:
        cs = re.findall("\d+", c)
        cs = cs if len(cs) > 0 else re.findall("\.", c)
        if len(cs) > 0:
            rs = rs + cs[0]
            
    if len(rs) > 0 :
        try:
            return float(rs)
        except:
            return float("0")
    return float("0")

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

dcfile = './cpu.json'
url = 'https://cpu.bmcx.com/web_system/bmcx_com_www/system/file/cpu/get_data/?lx=cpu&s=0&e=999999999&ajaxtimestamp='


def spider_td_txt(selector, field):
    try:
        sf = "//div[@id='main_content']//td[.='"+field+"']/following-sibling::*/text()"
        tdEl = selector.xpath(sf)
        if len(tdEl) > 0 :
            return tdEl[0]
        return ""
    except:
        return ""


def spider_json(o):
    response = requests.get(url + str(datetime.now().microsecond), timeout=(10, 10))
    cpus = json.loads(response.text)

    try:
        open(o, 'w').close()
        of = open(o,"a")
        count = 0
        try:
            t = len(cpus)
            b = 0
            print('start spider，Write is {}%'.format(b))
            for cpu in cpus:
                id = cpu['id']
                response = requests.get('https://cpu.bmcx.com/'+ str(id) +'__cpu/', timeout=(10, 10))
                selector = etree.HTML(response.text)
                cpu["发布时间"] = spider_td_txt(selector, "发布时间")
                cpu["TDP"] = strToFloat(spider_td_txt(selector, "TDP"))
                cpu["TDP Down"] = strToFloat(spider_td_txt(selector, "TDP Down"))
                cpu["得分"] = strToFloat(spider_td_txt(selector, "得分"))
                cpu["核心数"] = strToFloat(spider_td_txt(selector, "核心数"))
                cpu["线程数"] = strToFloat(spider_td_txt(selector, "线程数"))
                cpu["主频"] = strToFloat(spider_td_txt(selector, "主频"))
                cpu["睿频"] = strToFloat(spider_td_txt(selector, "睿频"))
                cpu["其它名称"] = spider_td_txt(selector, "其它名称")
                cpu["插槽类型"] = spider_td_txt(selector, "插槽类型")
                of.write(str(cpu) + '\n')
                count = count + 1
                c = round(count / t * 100, 2)
                if c - b > 5:
                    b = c
                    print('Write is {}%'.format(b))
        finally:
            of.close()
            print('Write is {} \n'.format(count))
    except IOError:
        print('Write failed')


# s为已存在的json数据文件，q为查询条件
def start(file, query, output):
    spider_json(output)





if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, required=False, default=dcfile, help="query local json data path, default is ./cpu.json")
    parser.add_argument("-q", "--query", type=str, required=False, default="df=1000&hxs=2&xcs=2&tdp=65&zp=1.0")
    parser.add_argument("-o", "--output", type=str, required=False, default=dcfile, help="output path, default is ./cpu.json")
    args = parser.parse_args()
    # try:
    print(args)
    start(args.file, args.query, args.output)
    print('Finished')
    # except:
    #     print('error')
