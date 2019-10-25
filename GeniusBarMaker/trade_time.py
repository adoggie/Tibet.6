#coding:utf-8
"""
2018/7/30  update
    未考虑集合竞价时间段的tick并入首个k线


（t1,t2,flag) :
    - flag :
        '-' 跨日交易
        '*' 包含集合竞价
"""
import fire
from logging import getLogger
from datetime import datetime as DateTime,timedelta as TimeDelta,time as Time
from dateutil.parser import parse
import os.path
from collections import  OrderedDict

trade_space_templates = {
        # 天然橡胶（RU）、螺纹钢（RB）热轧卷板（HC）、石油沥青（BU）
        'sf_1':{ 'p':'RU,RB,BU,HC',
                't':[
                        (Time(21,0),Time(23,0),120,'*'),
                        (Time(9,0),Time(10,15),75,'*'), # 75 表示事件周期（分钟) '*' : 开盘带有1分钟集合竞价的时间段 ; '-' : 跨日的时间段
                        (Time(10,30),Time(11,30),60),
                        (Time(13,30),Time(15,0,90)),

                    ],
                 'td':'trade_days.txt'
                 },
        # 铜（CU）、铝（AL）、锌（ZN）铅（PB）、镍（NI）、锡（SN）
        'sf_2':
            { 'p':'CU,AL,ZN,PB,NI,SN',
              't':
                [
                    (Time(21,0),Time(1,0),240,'*'),
                    (Time(9,0),Time(10,15),75,'*'),
                    (Time(10,30),Time(11,30),60,),
                    (Time(13,30),Time(15,0),90),

                ],
                'td':'trade_days.txt'
              },
        # 黄金（AU）、白银（AG）
        'sf_3':
            { 'p':'AU,AG',
              't':
                [
                    (Time(21,0),Time(2,30),330,'*'),
                    (Time(9,0),Time(10,15),75,'*'),
                    (Time(10,30),Time(11,30),60),
                    (Time(13,30),Time(15,0),90),

                ],
              'td':'trade_days.txt'
              },
        # 燃料油（FU）、线材（WR
        'sf_4':
            {'p': 'FU,WR',
             't':
                [    (Time(9,0),Time(10,15),75,'*'),
                     (Time(10,30),Time(11,30),60),
                     (Time(13,30),Time(15,0),90),
                ],
             'td':'trade_days.txt'
            },

        # 大商所
        # 棕榈油（P）、焦炭（J）、豆粕（M）豆油（Y）、豆一（A)、豆二(B) 焦煤(JM)、铁矿石(I)
        'ds_1':
            {'p': 'P,J,M,Y,A,B,JM,I',
             't':
                [
                    (Time(21, 0), Time(23, 30), 150,'*'),
                    (Time(9,0),Time(10,15),75,'*'),
                    (Time(10,30),Time(11,30),60),
                    (Time(13,30),Time(15,0),90),

                ],'td':'trade_days.txt'
             },
        # 胶合板(BB)、玉米(C)、玉米淀粉(CS) 纤维板(FB)、塑料(L)、聚丙烯(PP) 聚氯乙烯(V)、鸡蛋（JD）
        'ds_2':
            {'p': 'BB,C,CS,FB,L,PP,V,JD',
             't':
                [    (Time(9,0),Time(10,15),75,'*'),
                    (Time(10,30),Time(11,30),60),
                    (Time(13,30),Time(15,0),90),
                ],'td':'trade_days.txt'
             },
        # 郑商所
        # 白糖(SR)、棉花(CF)、菜粕(RM) 甲醇(MA)、PTA(TA)、动力煤(ZC) 玻璃(FG)、菜籽油(OI)、棉纱（CY）
        'zs_1':
            {'p': 'SR,CF,RM,MA,TA,ZC,FG,OI,CY',
             't':
                [    (Time(21,0),Time(23,30),150,'*'),
                     (Time(9,0),Time(10,15),75,'*'),
                    (Time(10,30),Time(11,30),60),
                    (Time(13,30),Time(15,0),90),

                ],'td':'trade_days.txt'
             },
        # 粳稻（JR）、晚籼稻（LR) 普通小麦(PM)、早籼稻(RI) 油菜籽(RS)、硅铁(SF) 锰硅(SM)、强麦(WH)
        'zs_2':
            {'p': 'JR,LR,PM,RI,RS,SF,SM,WH,AP',
             't':
                [    (Time(9,0),Time(10,15),75,'*'),
                    (Time(10,30),Time(11,30), 60),
                    (Time(13,30),Time(15,0), 90),
                ],'td':'trade_days.txt'
             },
        # 中金所
        # 沪深300(IF) 上证50(IH)、中证500(IC)
        'zj_1':
            {'p': 'IF,IH,IC',
             't':
                [   (Time(9,30),Time(10,15), 75,'*'),
                    (Time(10,30),Time(11,30), 60 ),
                    (Time(13,0),Time(15,0), 120),
                ],'td':'trade_days.txt'
             },

        # 五年期国债(TF)、十年期国债(T）
        'zj_2':
            {'p': 'TF,T',
             't':
                [   (Time(9,15),Time(10,15),60,'*'),
                    (Time(10,30),Time(11,30),60),
                    (Time(13,0),Time(15,15),135),
                    # (Time(13,0),Time(15,15)),
                ],'td':'trade_days.txt'
             },

        # 能源中心
        'ny_1':
            {'p': 'SC',
             't':
                [    (Time(21,0),Time(2,30),330,'*'),
                     (Time(9,0),Time(10,15), 75,'*'),
                    (Time(10,30),Time(11,30) , 60),
                    (Time(13,30),Time(15,0),90),

                ],'td':'trade_days.txt'
             },

        }

# 产品交易时段表
# AG:[(Time(9,0),Time(10,15)),..]
product_time_spaces = OrderedDict()
# 完成产品名称与交易日期的关联
# 'AG':{DateTime('2018-9-1'):0,DateTime('2018-9-2'):1}
product_trade_days =OrderedDict()

def index_product_trade_timespaces():
    """
    生成:  产品 <-> 交易时间段  匹配关系
    :return:

        'SC':  [    (Time(21,0),Time(2,30),330,'*'),
                     (Time(9,0),Time(10,15), 75,'*'),
                    (Time(10,30),Time(11,30) , 60),
                    (Time(13,30),Time(15,0),90),
            ]

    """
    result = product_time_spaces
    for k,v in trade_space_templates.items():
        t,p = v.get('t'),v.get('p')
        for s in  map(lambda x:x.strip().upper(),p.split(',')):
            result[s] = t
    return product_time_spaces

def index_product_trade_days(dir='./'):
    """
    产品交易日期
    {
     'AG':{'2018-9-1':0,'2018-9-2':1},..
     }
    """


    result = product_trade_days
    date_defs ={}

    for k,v in trade_space_templates.items():
        td,p = v.get('td'),v.get('p')
        for s in  map(lambda x:x.strip().upper(),p.split(',')):
            result[s] = td

        if not date_defs.has_key(td):
            lines = open(os.path.join(dir, td)).readlines()
            # 删除 空行 和注释行
            lines = filter(lambda _: _.strip() and _[0] != '#', lines)
            lines = map(lambda s: s.split()[0].strip(), lines)
            dates = [parse(ymd).date() for ymd in lines]
            dates = OrderedDict(zip(dates,range(len(dates))))
            date_defs[td] = dates  # dates: dict

    for name,td in product_trade_days.items():
        dates = date_defs.get(td,OrderedDict())
        product_trade_days[name] = dates
        # 到此，完成产品名称与交易日期的关联  'AG':{'2018-9-1':0,'2018-9-2':1}

    return product_trade_days

def get_trade_timespace_by_exchange(name):
    """根据交易所定义类型获得交易时间段"""
    return trade_space_templates.get(name,{}).get('t')

def get_trade_timespace_by_product(product):
    """name :  IF,T,SC,IC,...
        :return :
            [(Time(9,0),Time(10,15)), ..]
    """
    return product_time_spaces.get(product.upper())

def is_trade_day(date,product='M'):
    """判别指定的产品是否当日交易
    date - datetime.datetime
    """
    if isinstance(date,str):
        date = parse(date)
    days = product_trade_days.get(product,{})
    if days.has_key( date.date() ) :
        return True
    return False


def get_timespace_of_trade_day(date,product='M'):
    """
    根据指定的日期date ,返回此交易日的行情数据时间段(开始-结束)
    date的前一个交易日的夜盘开始  , 需要搜索前一个交易日的夜盘开始到本date交易日的下午收盘结束
    20:59(-1) - 15:30
    之前请务必清洗掉非正常行情交易tick
    :return [start,end)
        (2019-5-10 21：00 , 2019-5-11 15:30)
    """
    result =()
    if isinstance(date,str):
        date = parse(date)
    date = date.date()
    days = product_trade_days.get(product, {})
    sorted_days = days.keys()
    idx = sorted_days.index(date)
    if idx == -1: # 无效的交易日
        getLogger().error('date: {} is not defined in trade_days.txt'.format(str(date)))
        return ()
    start = date - TimeDelta(days=1)  # 默认前一天为前一个交易日
    if idx !=0: # 如果不是第一条日期记录则找前一条
        idx-=1
        start = sorted_days[idx]

    # 规定日线从前一个交易日的夜盘开始,到交易日(date)的下午收盘时间为止
    # start = DateTime.combine(start,Time(20,59,0,0))
    start = DateTime.combine(start,Time(21,0,0,0))
    date = DateTime.combine(date,Time(15,30,0,0))
    # start.replace(hour=20,minute=59,second=0,microsecond=0)
    # date.replace(hour=15,minute=30,second=0,microsecond=0) #
    return (start,date)

index_product_trade_timespaces()
index_product_trade_days()

if __name__ == '__main__':
    # print product_trade_days
    fire.Fire()
