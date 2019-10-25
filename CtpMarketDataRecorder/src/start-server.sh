#!/usr/bin/env bash
pwd=$(cd `dirname $0`;pwd)

echo $pwd
source ~/.bashrc
export PYTHONPATH=/home/samba/data/Porjects/Branches
export LANG="zh_CN.UTF-8"
export PYTHONIOENCODING=utf8
cd $pwd
python server-data-resource.py




