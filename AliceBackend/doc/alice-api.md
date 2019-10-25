
# Alice TradeData Api

```text
version : 0.1 
```
### 1. 查询交易日
**get_trade_days()**

```
Url: /fisher/api/trade_days
Method: GET
Input:

Output:
  - result  [] 交易日列表
      
Examples:
  { status:0 , result :[ '2019-5-02',..] }
```

### 2. 查询策略列表
**get_strategy_list()**

```
Url: /fisher/api/strategy/list
Method: GET 
Input:
  - date (str)  交易日
Output:
  - result  [] 列表
    - strategy_id 
    - comment
    - date   指定交易日
      
Examples:
  { status:0 , result :[ '2019-5-02',..] }
```

### 3. 获取策略运行证券代码列表
**get_code_list()**

```
Url: /fisher/api/strategy/code/list
Method: GET 
Input:
  - date (str)  交易日
  - strategy_id (str) 
Output:
  - result  [] 列表
    - code
    - name
    - price
      - last 
      - qty
      - diff
      - diff_rate
      - s1 .. s5
      - b1 .. b5
      - sq1 .. sq5
      - bq1 .. bq5
    - pos
      - qty_current 总持仓
      - qty_yd     昨仓
      - qty_td     今仓
      
      
Examples:
  { status:0 , result :[ '2019-5-02',..] }
```

### 4. 获取证券代码运行交易日志
**get_code_trade_logs()**

```
Url: /fisher/api/strategy/code/logs
Method: GET 
Input:
  - date (str)  交易日
  - strategy_id (str) 策略编号
  - code        股票代码
Output:
  - result  [] 列表
    - code
    - time 
    - event
    - time 
    - ...
      
Examples:
  { status:0 , 
    result :[ {} , ...] }
```