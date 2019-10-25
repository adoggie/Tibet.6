
##发布配置

设置环境变量 CAMEL_HOME 为指定运行的主目录，如不设置 则默认目录为 /srv/camel

设置环境变量 APP_NAME 为项目名称,例如:  carrier ,driver 

    export CAMEL_HOME=/srv/camel
    export APP_NAME=carrier_server
    
   

##开发配置 

####1.设置环境变量 CAMEL_HOME 为开发项目的目录
    
    export CAMEL_HOME=/home/scott/projects/carrier
    
 程序启动时在$CAMEL_HOME中自动创建目录: run, data, etc, logs 

####2.删除环境变量 APP_NAME 设置
####3.设置环境变量 CAMEL_LIB 
    
    export CAMEL_LIB=/Users/scott/Desktop/yto/svn/dev_package/python

####3.运行 run/start-server-dev.sh

##发布和开发配置区别

发布目录：

    /srv/camel
    ├── data
    │   └── carrier_server
    ├── etc
    │   └── carrier_server
    │       └── settings.yaml
    ├── logs
    │   └── carrier_server
    │       ├── server.log
    │       └── trans.log
    ├── products
    │   └── carrier_server
    └── run
        └── carrier_server
    
####开发目录

    /home/project/carrier_server/
    ├── data
    │   └── data.01
    ├── etc
    │   └── settings.yaml
    ├── logs
    │   ├── server.log
    │   └── trans.log
    ├── run
    │   ├── carrier.pid
    │   └── start-carrier.sh
    └── src
        ├── server.py
        └── service


开发目录详细

    test_project/
    ├── README.md
    ├── data
    ├── etc
    │   └── settings.yaml
    ├── logs
    │   ├── server.log
    │   └── trans.log
    ├── run
    ├── scripts
    ├── src
    │   ├── model
    │   │   └── __init__.py
    │   ├── route
    │   │   ├── __init__.py
    │   │   └── v1
    │   │       ├── __init__.py
    │   │       └── car.py
    │   ├── server.py
    │   └── service
    │       └── __init__.py
    └── tests
        └── test_run.py


##Blueprint设置 

flask 的blueprint 通过settings.yaml 的blueprints项配置适当的 条目即可

     blueprint_routes:
      - package: 'access.api.v1'
        url: '/v1'
        modules:
          - name: 'car'
            url: '/car'
            routes:
              - url: '/cat'   # url name
                name: 'cat'   # function name
                methods: 'GET,POST'
              - url: '/online'
                name: 'lines'
        
    >>  wget http://127.0.0.1:5000/v1/car/
    >> 'okay'
    

flask-sqlalchemy