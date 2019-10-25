#!/usr/bin/env bash

pid=`ps -eaf | grep geniusbarmaker | grep -v grep | awk '{print $2}' `
echo $pid
kill -9 $pid

pid=`ps -eaf | grep server-data-resource.py | grep -v grep | awk '{print $2}' `
echo $pid
kill -9 $pid


pid=`ps -eaf | grep CtpTrade-zsqh-prd | grep -v grep | awk '{print $2}' `
echo $pid
kill -9 $pid

pid=`ps -eaf | grep CtpMarket-zsqh-prd | grep -v grep | awk '{print $2}' `
echo $pid
kill -9 $pid

