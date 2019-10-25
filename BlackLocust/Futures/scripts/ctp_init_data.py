#coding:utf-8
"""
初始化策略运行控制参数
"""

from collections import OrderedDict
from mantis.sg.fisher import stbase

"""
定义所有证券代码信息

)交易所编号ExchangeID全部大写CFFEX、CZCE、DCE、INE、SHFE;

"""
CODES={
        'i2001': {'name':u'i2001','exchange':'DCE'} ,
        'jm2001': {'name': u'jm2001','exchange':'DCE'} ,

        'SR001': {'name':u'SR001','exchange':'CZCE'} ,
        'TA001': {'name':u'TA2001','exchange':'CZCE'} ,    #
        # 'IF2003': {'name':u'IF2003','exchange':'CFFEX'} ,

        'j2001': {'name': u'j2001','exchange':'DCE'} ,
        'rb2001': {'name': u'rb2001','exchange':'SHFE'} ,
        'ru2001': {'name': u'ru2001','exchange':'SHFE'} ,

       }

CODES_TRADING = {
}

# CODES.update( CODES_TRADING)
# CODES_INIT_POS = copy.deepcopy(CODES_TRADING)   # 初始化持仓的票
CODE_CLEARS = False  # 初始化清除所有商品代码信息

# 所有运行策略定义列表
strategies = [

    dict(
        strategy_id= 'ctp_day_spear_i2001',   # 策略编号
        conn_url='zsqh-prd' ,         # 账户链接信息
        script='ctp_real_dayspear_run.py',
        run_test_params='',
        run_real_params='run',
        codes=[
            dict(
                name = 'i2001',
                _renew = False,   # 防止再次运行参数被复写
                STOP_WIN=22,
                STOP_WIN_MIN=20,
                TIMEPERIOD = 10,
                N = 1,
                DATASET = "",             # 行情记录集名称
                LOT_PER_UNIT =  100,          # 每收交易乘数
                FEE_HOP =  5,               # 手续费每跳
                PRICE_HOP = 1,
                MARGIN_RATIO =  0.05,       # 保证金比例
                MAX_MARGIN_AMOUNT = 0.2,     # 最大保证金占用总资金比值
                HIST_DATA_START = '2019-1-1',   # 历史数据加载
                HIST_DATA_END = '',

                direction = stbase.Constants.Idle,
                open_days = 0 ,     # 持仓数
                open_date = None,     # 开仓日期
                sub_tick =1,        # 订阅tick
            )
        ],
        enable = 1,run = 1,comment = u'日k均线平滑移动交易日趋势收敛'
    ),
    dict(
        strategy_id= 'ctp_day_spear_SR001',   # 策略编号
        conn_url='zsqh-prd' ,         # 账户链接信息
        script='ctp_real_dayspear_run.py',
        run_test_params='',
        run_real_params='run',
        codes=[
            dict(
                name ='SR001',
                clone_from = 'ctp_day_spear_i2001/i2001', # 合约参数从指定策略赋值
                # STOP_WIN = 28,  # 再次覆盖
            )
        ,
            # dict(
            #     name ='ru2002',
            #     clone_from = 'ru2001', # 合约参数从指定策略赋值
            #     STOP_WIN = 28,  # 再次覆盖
            # )
        ],
        enable = 1,run = 1,comment = u'日k均线平滑移动交易日趋势收敛'
    ),

    dict(
        strategy_id= 'ctp_day_spear_TA001',   # 策略编号
        conn_url='zsqh-prd' ,         # 账户链接信息
        script='ctp_real_dayspear_run.py',
        run_test_params='',
        run_real_params='run',
        codes=[
            dict(
                name = 'TA001',
                clone_from = 'ctp_day_spear_i2001/i2001',
                PRICE_HOP = 2
            )
        ],
        enable = 1,run = 1,comment = u'日k均线平滑移动交易日趋势收敛'
    ),


    dict(
        strategy_id='ctp_day_spear_j2001',  # 策略编号
        conn_url='zsqh-prd',  # 账户链接信息
        script='ctp_real_dayspear_run.py',
        run_test_params='',
        run_real_params='run',
        codes=[
            dict(
                name='j2001',
                clone_from='ctp_day_spear_i2001/i2001'
            )
        ],
        enable=1, run=1, comment=u'日k均线平滑移动交易日趋势收敛'
    ),

    dict(
        strategy_id='ctp_day_spear_rb2001',  # 策略编号
        conn_url='zsqh-prd',  # 账户链接信息
        script='ctp_real_dayspear_run.py',
        run_test_params='',
        run_real_params='run',
        codes=[
            dict(
                name='rb2001',
                clone_from='ctp_day_spear_i2001/i2001'
            )
        ],
        enable=1, run=1, comment=u'日k均线平滑移动交易日趋势收敛'
    ),

    dict(
        strategy_id='ctp_day_spear_ru2001',  # 策略编号
        conn_url='zsqh-prd',  # 账户链接信息
        script='ctp_real_dayspear_run.py',
        run_test_params='',
        run_real_params='run',
        codes=[
            dict(
                name='ru2001',
                clone_from='ctp_day_spear_i2001/i2001'
            )
        ],
        enable=1, run=1, comment=u'日k均线平滑移动交易日趋势收敛'
    ),

    dict(
        strategy_id='ctp_day_spear_jm2001',  # 策略编号
        conn_url='zsqh-prd',  # 账户链接信息
        script='ctp_real_dayspear_run.py',
        run_test_params='',
        run_real_params='run',
        codes=[
            dict(
                name='jm2001',
                clone_from='ctp_day_spear_i2001/i2001'
            )
        ],
        enable=1, run=1, comment=u'日k均线平滑移动交易日趋势收敛'
    ),

]
