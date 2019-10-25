

ctpMarketDataRecorder 
------
获取ctp市场行情Tick数据，转发到缓存系统

接收的行情数据包括: 

- tick
- bar (1,3,5,15,30,60)

```html
消息发布到以下通道 

ctp.pub_depthmarket = ctp.pub_*       redis.publish()
ctp.list_depthmarket = ctp.list_all   redis.rpush()
ctp.last_depthmarket = ctp.dm_*       redis.hmset() 

<*> 表示具体的合约代码


```