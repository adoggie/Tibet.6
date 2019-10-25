
GeniusBarMaker v1.1
-------
Ctp 行情k线计算服务 (改进版本)



1. geniusbarmaker.py   k线计算主程序。 等待行情推送tick到redis的publish通道 `ctp.tick.pub`。
读取tick 缓存并计算出 1,5,15,30,60分钟的周期k线，并发送到redis的publish
通道`ctp.bar.pub`,待 `CtpMarketRecorder`读取并持久化k线到mongodb。

2. make-day-bar.py , make-min-bar.py, make-all-bar.py  
分别执行 分钟，日线的计算
make-day-bar.py , make-min-bar.py 支持一个参数带入， symbol

`python make-min-bar.py TA001 2019-1-1`

make-all-bar.py 扫描当前Ctp_Tick中所有合约，一次执行所有分钟，日线计算


作废!! 2. playTick.py  当main.py并不能接收全部的开盘tick时，需要在盘后重新生成当日所有k线记录，这就需要
`playTick.py`读取当日的tick，并再次发送给 `main.py`进行处理。 

## 配置

> `config.py` 修改`redis_host`,`host`和响应的端口。 redis: 6379 , mongodb:27017
`config.REAL` 盘中运行时需打开 REAL ，将定时产生分钟`break`信号，触发前一个k线周期结束



    # 这个DateTime 是交易日YMD+ 当日HMS
    # 恶心的问题，在于非交易时间接收的tick的HMS居然也是错误的，shit，所以过滤是否有效tick要判断SaveTime字段了
    
    下午15点之后收到的tick 时分秒居然是上午10点左右的tick，混乱
    所以 要以接收SaveTime进行过滤， 这就要求主机时钟必须一致了。