#!/usr/bin/env bash

# 启动每日收盘之后的日线数据同步

pwd=$(cd `dirname $0`;pwd)

source ~/.bashrc
export PYTHONPATH=/home/samba/data/Porjects/Branches/pythonlibs
export LANG="zh_CN.UTF-8"
export PYTHONIOENCODING=utf8

cd $pwd
echo  `pwd`
python futures_hq_daily_crawler.py






