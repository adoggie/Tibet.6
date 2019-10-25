#coding:utf-8

"""
第三方网站爬取日行情数据
"""

import os,os.path

import config
# import ctp_init_calender

import requests
from mantis.sg.fisher import stbase

#
import datetime,time,traceback
from dateutil.parser import parse
import pymongo

"""
https://www.jb51.net/article/140239.htm

Selenium2+python自动化45-18种定位方法（find_elements）
https://www.cnblogs.com/yoyoketang/p/6557421.html  

https://chromedriver.chromium.org/downloads

"""


conn = pymongo.MongoClient(config.MONGODB[0], config.MONGODB[1])


def crawl_it(symbol):
    from selenium import webdriver

    print 'Crawling ',symbol,'..'
    base_url = 'https://finance.sina.com.cn/futures/quotes/{}.shtml'.format(symbol)
    print base_url
    # driver = webdriver.Chrome('/Users/scott/Desktop/Projects/Selenium/chrome_77/chromedriver')
    driver = webdriver.Chrome('E:/Tools/chromedriver_win32/chromedriver.exe')
    driver.set_page_load_timeout(5)
    driver.set_script_timeout(5)

    driver.get(base_url)
    path = '''#table-box-futures-hq > tbody > tr:nth-child(1) > td.price.green'''

    path = '''#table-box-futures-hq > tbody > tr:nth-child(1) > td.price'''

    lastest = driver.find_element_by_css_selector(path).text

    open = driver.find_element_by_css_selector(
        '''#table-box-futures-hq > tbody > tr:nth-child(1) > td.open-price''').text

    open = driver.find_element_by_css_selector(
        '''#table-box-futures-hq > tbody > tr:nth-child(1) > td.open-price''').text
    high = driver.find_element_by_css_selector(
        '''#table-box-futures-hq > tbody > tr:nth-child(1) > td.max-price''').text
    low = driver.find_element_by_css_selector('''#table-box-futures-hq > tbody > tr:nth-child(1) > td.min-price''').text
    close = lastest

    vol = driver.find_element_by_css_selector('''#table-box-futures-hq > tbody > tr:nth-child(2) > td.volume''').text



    print open, high, low, close,vol
    # driver.implicitly_wait()
    driver.close()
    return  open, high, low, close,vol


def crawl_it_sina(symbol):
    print 'Crawling ',symbol,'..'
    base_url = 'http://hq.sinajs.cn/?format=text&list={}'.format(symbol)
    print base_url
    resp = requests.get(base_url)
    _,fs = resp.text.strip().split('=')
    fs = fs.split(',')
    open,high,low,close,vol,openinterest = fs[2],fs[3],fs[4],fs[7],fs[14],fs[13]
    return open,high,low,close,vol

def get_daily_data():
    """进行爬取上一个交易日的行情日线"""
    for symbol,tag in config.CRAWL_DAILY_SYMBOLS.items():
        last = None
        for i in range(5):
            try:
                last = crawl_it_sina(tag)
                break
            except:
                traceback.print_exc()
                print 'Wait a while ..'
                time.sleep(5)
        if not last:
            print 'Crawl Quotes Error , Broken Out.'
            return

        coll = conn['Ctp_Bar_d'][symbol]
        date = datetime.datetime.now()
        date = date.replace(hour=0,minute=0,second=0,microsecond=0)
        r = coll.find_one({'datetime':date})
        if r:
            coll.delete_one({'_id':r['_id']})
        r = None
        if not r:

            bar = stbase.BarData()
            bar.code = symbol
            bar.cycle = 'd'
            bar.open = float(last[0])
            bar.high = float(last[1])
            bar.low = float(last[2])
            bar.close = float(last[3])
            bar.vol = float(last[4])
            bar.amount = float(0)
            bar.time = date
            bar.datetime = bar.time

            print bar.dict()
            coll.insert(bar.dict())


def is_trading_day():
    now = datetime.datetime.now()
    today = now.replace(hour=0,minute=0,second=0,microsecond=0)
    dayfile = os.path.join(  os.path.dirname( os.path.abspath(__file__)), 'trading-days.txt')
    lines = open(dayfile).readlines()
    lines = map(lambda _:_.strip(),lines)
    lines = filter(lambda _:len(_),lines)
    for line in lines:
        day = parse(line)
        if day == today:
            return True
    return False

def start():
    now = datetime.datetime.now()
    if now.time() < datetime.time(config.CRAWL_WORKTIME[0]) or \
        now.time() > datetime.time(config.CRAWL_WORKTIME[1]) :
        print 'Error: Not In work Time , passed..'
        return


    if is_trading_day():
        get_daily_data()




start()