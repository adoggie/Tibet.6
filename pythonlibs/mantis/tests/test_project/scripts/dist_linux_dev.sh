#!/bin/bash

pwd=$(cd `dirname $0`;pwd)
alias cp='cp -f'
#alias cp='rsync'
#alias rsync='rsync -r'

#SERVICE_DIR=$(echo $1)/services

RELEASE_DIR=$pwd/../release

if [ $# == 0 ]; then
  echo 'Warning: params is 0, release path is [ ../release ]'
else
  RELEASE_DIR=$(echo $1)
fi

LEMON_DIR=$(echo $RELEASE_DIR)/lemon
echo $RELEASE_DIR

CAMEL_HOME=$RELEASE_DIR/camel

mkdir -p $CAMEL_HOME/data
mkdir -p $CAMEL_HOME/etc
mkdir -p $CAMEL_HOME/logs
mkdir -p $CAMEL_HOME/run
mkdir -p $CAMEL_HOME/products

PRODUCT=$(cat $pwd/VERSION)


sed -e "s/##APP_NAME##/export APP_NAME=$PRODUCT/"  $pwd/../run/start-server-dev.sh > $CAMEL_HOME/run/$PRODUCT/start-server-dev.sh
sed -e "s/##APP_NAME##/export APP_NAME=$PRODUCT/"  $pwd/../run/start-server-uwsgi.sh > $CAMEL_HOME/run/$PRODUCT/start-server-uwsgi.sh

rsync -rvt $pwd/../etc/* $CAMEL_HOME/etc/$PRODUCT
#rsync -rvt $pwd/../run/* $CAMEL_HOME/run/$PRODUCT
rsync -rvt $pwd/../src/* $CAMEL_HOME/products/$PRODUCT

