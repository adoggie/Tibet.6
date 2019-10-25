#coding:utf-8


"""
ctp策略运行加载器定义

"""

from pymongo import MongoClient


from mantis.sg.fisher.utils.importutils import import_module
from mantis.sg.fisher.utils.useful import singleton
from mantis.fundamental.utils.timeutils import current_date_string

from mantis.sg.fisher import stbase
from mantis.sg.fisher import ams
from mantis.sg.fisher import strecoder
from mantis.sg.fisher import stsim
from mantis.sg.fisher import stgenerator

from mantis.sg.fisher.model import model
from mantis.sg.fisher.ctp.backtest import CtpMarketBarBackTest,CtpTraderBackTest
from mantis.sg.fisher import stutils
from mantis.sg.fisher.stbase.loader import StrategyLoader

class CtpBackTestLoader(StrategyLoader):
    """回测加载器类"""
    def __init__(self):
        StrategyLoader.__init__(self)
        self.cfgs = {}

    def load(self,strategy_id,
             strategy_cls,
             symbol,
             strategy_db=('127.0.0.1',27017),
             dbname='TradeFisherCtp',
             quotes_db=('127.0.0.1',27017),
             cycle=1, start='2019-6-18 9:0', end='2019-6-19 15:0', freq=.1):
        """

        :param strategy_id:     策略编号
        :param strategy_cls:    策略类定义
        :param symbol:          商品合约代码
        :param strategy_db:     策略运行数据库(host,port)
        :param dbname:          策略运行数据库名
        :param quotes_db:       行情数据库
        :param cycle:           K线周期 1,5,15,30
        :param start:           回测加载数据开始时间
        :param end:             回测加载数据结束时间
        :param freq:            K线回放速度控制 .1 s
        :return:
        """

        SYMBOL = symbol
        mongodb_host, mongodb_port = strategy_db
        data_path = './'+strategy_id
        quotas_db_conn = MongoClient(quotes_db[0], quotes_db[1])  # 历史k线数据库

        # 初始化系统参数控制器
        paramctrl = stbase.MongoParamController()
        paramctrl.open(host=mongodb_host, port=mongodb_port, dbname=dbname)
        # 策略控制器
        stbase.controller.init(data_path)
        # 添加运行日志处理
        stbase.controller.getLogger().addAppender(stbase.FileLogAppender('CTP'))
        stbase.controller.setParamController(paramctrl)

        param = paramctrl.get(strategy_id)  # 读取指定策略id的参数
        # conn_url = paramctrl.get_conn_url(param.conn_url)   # 读取策略相关的交易账户信息

        # 初始化行情对象
        params = dict(db_conn=quotas_db_conn, cycle= cycle, symbol=SYMBOL,
                      start=start, end=end, freq=freq)
        # params.update( conn_url.dict() )
        market = CtpMarketBarBackTest().init(**params)  # 配置历史行情记录加载器
        # 装备行情对象到股票产品
        stbase.controller.futures.setupMarket(market)
        # 初始化交易对象
        # trader = CtpTrader().init(**conn_url.dict())
        trader = CtpTraderBackTest().init()
        stbase.controller.futures.setupTrader(trader)

        # 初始化策略对象
        strategy = strategy_cls(strategy_id, stbase.controller.futures).init().setLoader(self)

        # 设置策略日志对象
        strategy.getLogger().addAppender(
            strecoder.StragetyLoggerMongoDBAppender(db_prefix=dbname, host=mongodb_host, port=mongodb_port))
        # 添加策略到 控制器
        stbase.controller.addStrategy(strategy)
        self.strategy = strategy

        return self

    def getTradeObject(self,bar):
        """模拟获得当前最新的Tick数据"""
        tradeobj = self.strategy.product.getTradeObject(bar.code)
        tradeobj.price.LastPrice = bar.close
        tradeobj.price.AskPrice1 = bar.close
        tradeobj.price.BidPrice1 = bar.close
        return tradeobj

    def run(self):
        # 控制器运行
        stbase.controller.run()  # 开始运行 ，加载k线数据


class CtpStrategyLoader(StrategyLoader):
    """策略加载器类"""
    def __init__(self):
        StrategyLoader.__init__(self)
        self.cfgs = {}

    def load(self,strategy_id,
             strategy_cls,
             symbol,
             strategy_db=('127.0.0.1',27017),
             dbname='TradeFisherCtp',
             quotes_db=('127.0.0.1',27017),
             cycle=1, start='2019-6-18 9:0', end='2019-6-19 15:0', freq=.1):
        """

        :param strategy_id:     策略编号
        :param strategy_cls:    策略类定义
        :param symbol:          商品合约代码
        :param strategy_db:     策略运行数据库(host,port)
        :param dbname:          策略运行数据库名
        :param quotes_db:       行情数据库
        :param cycle:           K线周期 1,5,15,30
        :param start:           回测加载数据开始时间
        :param end:             回测加载数据结束时间
        :param freq:            K线回放速度控制 .1 s
        :return:
        """

        SYMBOL = symbol
        mongodb_host, mongodb_port = strategy_db
        data_path = './'+strategy_id
        quotas_db_conn = MongoClient(quotes_db[0], quotes_db[1])  # 历史k线数据库

        # 初始化系统参数控制器
        paramctrl = stbase.MongoParamController()
        paramctrl.open(host=mongodb_host, port=mongodb_port, dbname=dbname)
        # 策略控制器
        stbase.controller.init(data_path)
        # 添加运行日志处理
        stbase.controller.getLogger().addAppender(stbase.FileLogAppender('CTP'))
        stbase.controller.setParamController(paramctrl)

        param = paramctrl.get(strategy_id)  # 读取指定策略id的参数
        # conn_url = paramctrl.get_conn_url(param.conn_url)   # 读取策略相关的交易账户信息

        # 初始化行情对象
        params = dict(db_conn=quotas_db_conn, cycle= cycle, symbol=SYMBOL,
                      start=start, end=end, freq=freq)
        # params.update( conn_url.dict() )
        market = CtpMarketBarBackTest().init(**params)  # 配置历史行情记录加载器
        # 装备行情对象到股票产品
        stbase.controller.futures.setupMarket(market)
        # 初始化交易对象
        # trader = CtpTrader().init(**conn_url.dict())
        trader = CtpTraderBackTest().init()
        stbase.controller.futures.setupTrader(trader)

        # 初始化策略对象
        strategy = strategy_cls(strategy_id, stbase.controller.futures).init().setLoader(self)

        # 设置策略日志对象
        strategy.getLogger().addAppender(
            strecoder.StragetyLoggerMongoDBAppender(db_prefix=dbname, host=mongodb_host, port=mongodb_port))
        # 添加策略到 控制器
        stbase.controller.addStrategy(strategy)
        self.strategy = strategy

        return self

    def getTradeObject(self,bar):
        tradeobj = self.strategy.product.getTradeObject(bar.code)
        return tradeobj

    def run(self):
        # 控制器运行
        stbase.controller.run()  # 开始运行 ，加载k线数据




"""
mnogodb query statements
----------------------
db.getCollection('AJ_Test1_20190426').find({event:{$in:['order','order_cancel']}},{order_id:1,direction:1,code:1,price:1,oc:1,time:1,quantity:1,_id:0,event:1}).sort({time:-1})

"""