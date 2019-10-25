
### HTTP 接口

#### 1. 查询资金账户

```
Url : /ctp/account
Method : GET

```

#### 3. 持仓记录

```
Url : /ctp/position/list
Method : GET

```

#### 4. 订单记录

```
Url : /ctp/order/list
Method : GET

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
sdfasdajsdh
```


#### 7. 订单撤销

```
Url : /ctp/order/cancel
Method : POST


Remarks:

OrderID Specifiction:
    UserOrderId : A-FrontID-SessionID-OrderRef
    SysOrderId : B-ExchangeID-OrderSysID
    
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
