#!/usr/bin/env bash


pwd=$(cd `dirname $0`;pwd)

cd $pwd

cat $1.pid | xargs kill -9
#nohup python $1 $2 &