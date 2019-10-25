
# AliceBackend 
策略运行后台服务

- 监测运行策略的情况，包括：价格、持仓等

# WebApp Templates

- etc  程序配置目录
    - settings.yaml  主配置文件
- src  程序代码目录
    - http web程序目录
        - api.py    REST 接口
        - views.py  HTML 视图接口
        - token.py  令牌处理 
    - static  Web前端静态资源 (js,image,txt,..)
    - templates         Html 页面
    main.py             主服务入口
    server-webapp.py    服务加载
- tests   测试和初始化脚本 

- build_dist.sh     发布打包脚本

 



