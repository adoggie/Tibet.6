#!/usr/bin/env bash



pwd=$(cd `dirname $0`;pwd)

bash $pwd/stop_server.sh

cd $pwd/market
chmod +x CtpMarket-zsqh-prd
nohup ./CtpMarket-zsqh-prd &

cd $pwd/trader
echo `pwd`
chmod +x CtpTrade-zsqh-prd
nohup ./CtpTrade-zsqh-prd &



echo $pwd

source ~/.bashrc
export PYTHONPATH=$pwd/pythonpath
export LANG="zh_CN.UTF-8"
export PYTHONIOENCODING=utf8

cd $pwd/geniusbar
nohup python geniusbarmaker.py &

cd $pwd/datarecorder/src
nohup python server-data-resource.py &





