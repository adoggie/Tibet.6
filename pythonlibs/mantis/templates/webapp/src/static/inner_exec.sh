#!/usr/bin/env bash
uptime=`uptime | busybox awk -F ',' '{print $1}'`
ip=`/system/bin/busybox ip addr | /system/bin/busybox grep inet | /system/bin/busybox grep -v 127 | /system/bin/busybox grep -v inet6 | busybox awk '{print $2}'| busybox awk -F '/' '{print $1}'`
appver=`dumpsys package com.bc.keshiduijiang.pad | grep "versionName" | busybox awk -F '=' '{print $2}'`
echotest=`ls /system/xbin | grep echo_test`
echo $echotest
echo $appver
echo $ip
echo $uptime

wget --post-data="ip=${ip}&appver=${appver}&uptime=${uptime}&echotest=${echotest}" http://11.0.0.22:18080/api/innerbox/check

