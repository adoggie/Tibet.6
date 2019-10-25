
# Tibet_0.6
## 环境配置

0. Redis / MongoDB 
> 安装 redis 和 mongodb
```bash
    redis-server 
    mongod --dbpath=./data 
```

1. CtpMaket 
> 编辑 settings.txt  指定对应的ctp服务器地址端口和登录用户名

2. CtpTrade
> 编辑 settings.txt 

`端口: 17001`

3. CtpMarketDataRecorder 
> 编辑  $/etc/settings.yaml , 指定 `datasources/mongodb/host|port`, `message_brokers/redis/host|port`

4. GeniusBarMaker
> 编辑 $/config.py , 指定 `broker_url`为redis 主机链接， `db_host` 为 mongodb 主机链接

5. Latchet 
> 编辑 $/etc/settings.yaml  , 指定 `datasources/mongodb/host|port`, `message_brokers/redis/host|port`
指定
`服务端口: 18808`

6. AliceBackend
>  编辑 $/etc/settings.yaml  , 指定 `datasources/mongodb/host|port`, `message_brokers/redis/host|port`。

指定 `services/main/locust_home` 为 策略服务主目录 ，例如: `~/Desktop/Projects/Branches/Tibet_0.6/BlackLocust/Futures`
指定 `services/main/subscribed_symbols` 为行情tick订阅条目
指定 `services/main/latchet_server` 为消息推送服务地址 ，例如 : `'http://192.168.99.20:18808'`
>  edit  `Futures/scripts/config.py ` ,  填写正确的  mongodb /redis / td_api_url 地址参数。
初始化数据 `Futures/scripts/ctp_init_data.py , ctp_init_account.py , ctp_init_codes.py , start-futures-daybar-sync.sh`

```
1.历史k线数据导入和爬取 参数设置
config.py >> symbol
config.py >> CRAWL_DAILY_SYMBOLS #爬取日k线数据
```

导入历史k线: `python tdx_quote_import.py `

爬取一次最新的日k线记录 `python  futures_hq_daily_crawler.py `
启动自动爬取日k线 : 
```angular2
0 16 * * * /home/samba/data/Porjects/Branches/Tibet_0.5/Experiments/Futures/start-futures-daybar-sync.sh 
0 17 * * * /home/samba/data/Porjects/Branches/Tibet_0.5/Experiments/Futures/start-futures-daybar-sync.sh
0 18 * * * /home/samba/data/Porjects/Branches/Tibet_0.5/Experiments/Futures/start-futures-daybar-sync.sh


```

`服务端口: 7788` 



Ctp python编译
------
1. 官方提供的ctp 库文件 `libthostmduserapi.so`,`libhosttraderapi.so`,但未提供
`vnctptd.so`,   `vnctpmd.so`的python封装库。这两个需要用户自行编译。 

环境：

    Centos 7.3
    Python 2.7.14 / anaconda 2.7.14
    Boost 1.59 
    Cmake 2.8+
    
    > yum install python-devel

Boost: 

    Download boost 
    ./boostrap.sh —with-python=/usr/local/bin/python
    ./b2
    ./b2 install 

Vnctpmd.so/VnctpTd.so
    
    修改 CMakeLists.txt  
    保证： 
        find_package(Boost 1.59.0 COMPONENTS ..
        PYTHON_INCLUDE_PATH 为 /usr/local/include/python2.7 
        
    > cd vnpy/api/ctp
    > bash ./build.sh
    
TA-lib
    
    下载： 
    ta-lib-0.4.0-src.tar.gz （ source code 官网)
    TA-Lib-0.4.16.tar.gz    (python 接口封装 pypi.python.org)
    
    > tar xvzf ta-lib-0.4.0-src.tar.gz
    > ./configure & make & make install 
    
    > pip install TA-Lib-0.4.16.tar.gz
    
将以上编译和相关的库.so 全部安装或拷贝到 /usr/local/lib 

修改 `~/.bash_profile ` ,添加环境变量

    export LD_LIBRARY_PATH=/usr/local/lib
    eexport PYTHONPATH=<Tibet目录>
    