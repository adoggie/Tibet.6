#!/usr/bin/env bash


pwd=$(cd `dirname $0`;pwd)

cd $pwd
#python $1 $2 $3
nohup python $1 $2 $3 &

