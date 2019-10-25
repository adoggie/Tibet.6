
脚本说明:

1.build_dish.sh 

* 编译打包程序到 ./dist 目录 

2. crontab.sh 
* 复制定时计划执行任务，根据交易时间自动停/启服务

3. start_server.sh / stop_server.sh 
* 启动和停止所有服务


---
## 运行配置说明 
**Abouts Configurations**

vi /opt/tibet/market/settings.txt 
vi /opt/tibet/trader/settings.txt 

Market
- Redis :  

```
redis.host= 127.0.0.1
redis.port= 6379
```

Trader: 

- `ctp.require_auth = true` MUST be set in Product Envirotment.

 


