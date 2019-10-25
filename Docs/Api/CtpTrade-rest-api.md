
### HTTP 接口

#### 1. 查询资金账户

```
Url : /ctp/account
Method : GET

Remarks:
    stbase.futures.AccountStat    
```

#### 3. 持仓记录

```
Url : /ctp/position/list
Method : GET

Response:   stbase.futures.Position
    - InstrumentID = ''
    - PosiDirection = ''
    - HedgeFlag = ''
    - PositionDate = 0
    - YdPosition = 0     # 昨苍
    - Position = 0       # 今日持仓
    - LongFrozen = 0     # 多头冻结
    - ShortFrozen = 0    # 空头冻结
    - LongFrozenAmount = 0   # 开仓冻结金额
    - ShortFrozenAmount = 0  # 空仓冻结金额
    - OpenVolume = 0     # 开仓量
    - CloseVolume = 0    # 平仓量
    - OpenAmount = 0     # 开仓金额
    - CloseAmount = 0    # 平仓金额
    - PositionCost = 0   # 持仓成本 持仓均价
    - PreMargin = 0      # 上次占用的保证金
    - UseMargin = 0      # 占用的保证金
    - FrozenMargin = 0   # 冻结的保证金
    - FrozenCash = 0     # 冻结的资金
    - FrozenCommission = 0   # 冻结的手续费
    - CashIn = 0         # 资金差额
    - Commission = 0     # 手续费
    - CloseProfit = 0    # 平仓盈亏
    - PositionProfit = 0 # 持仓盈亏
    - TradingDay = 0     # 交易日
    - SettlementID = 0   # 结算编号
    - OpenCost = 0       # 开仓成本
    - ExchangeMargin = 0 # 交易所保证金
    - TodayPosition = 0  # 今日持仓
    - MarginRateByMoney = 0  # 保证金率
    - MarginRateByVolume = 0 # 保证金率(按手数)
    - ExchangeID = 0     # 交易所代码
    - YdStrikeFrozen = 0 # 执行冻结的昨仓
    
```

#### 4. 订单记录

```
Url : /ctp/order/list
Method : GET
Parameters:
 - user_no      formats: A#17#-147761744#6 /	A.17.-147761744.6
 - trans_no     B#CZCE#2019102309638903
```


#### 5. 成交记录

```
Url : /ctp/trade/list
Method : GET

```

#### 6. 订单委托

```
Url : /ctp/order/send
Method : POST
Parameters:
 - instrument 合约代码
 - price        价格
 - volume       量
 - direction    方向  sell/buy
 - oc           开平方向 open/close/forceclose/closetoday/closeyesterday
 - price_type   价格类型 
 - exchange_id  交易所编码 CZCE,DCE,SHFE,..

Remarks: 
    #任意价 AnyPrice = '1'
    #限价  LimitPrice = '2'
    #最优价 BestPrice = '3'
    #最新价 LastPrice = '4'
```


#### 7. 订单撤销

```
Url : /ctp/order/cancel
Method : POST
Paramters:
  - order_id  订单编号 'a-b-c-d' 

Remarks:

OrderID Format:
    UserOrderId : A-FrontID-SessionID-OrderRef
    SysOrderId : B-ExchangeID-OrderSysID
    
  Field 'a':
    - 'a' - 'A'  
      'b' - front_id
      'c' - session_id 
      'd' - order_ref 
    - 'a' - 'B'
      'b' - exchange 
      'c' - order_sys_id 
      'd' - unused 
      
订单编号有trade服务sendOrder时生成,支持两种格式（A或B）    
    
```

#### 8. 查询合约信息 （ 手续费、保证金 ...）

```
Url : /ctp/instrument/detail
Method : GET
Query Parameter :
  - instrument  合约名称

Response
  - result    {} 
    - instrument
    - margin
    - commission
     
```

#### 9. 执行一次合约查询 

```
Url : /ctp/instrument/query
Method : POST
Query Parameter :
  - instrument  合约名称
```
