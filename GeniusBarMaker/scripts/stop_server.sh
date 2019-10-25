#!/usr/bin/env bash

pid=`ps -eaf | grep geniusbarmaker | grep -v grep | awk '{print $2}' `

echo $pid
kill -9 $pid

