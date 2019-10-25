
CtpTradeCxx
========
ctp期货交易接口服务

1.

install 
=====


    yum install hiredis-devel


third-libs
=====

1. Redis-plusplus


    https://github.com/redis/hiredis.git
    https://github.com/sewenew/redis-plus-plus
    
    1.download hiredis , extract it and make install 
    2.download redis-cpp , extract it , mkdir build , cd build; cmake ..; make install
    
    
2. jsoncpp 


    http://open-source-parsers.github.io/jsoncpp-docs/doxygen/class_json_1_1_value.html
    

debug tools
====

    1. redis-cli  info / monitor


Problems Resolved:
==========
1. gdb SIGUSR1 break

vim ~/.gdbinit
  handle SIGUSR1 noprint nostop



编译说明:
=======
1. cmake3
2. mkdir build; cd build ; cmake3 -Dzsqh_test=ON -Dsimnow=OFF -Dzsqh_prd=ON ../