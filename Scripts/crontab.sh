#!/usr/bin/env bash


crontab -e

add following script lines.

55 8 * * *  /opt/tibet/start_server.sh
5 12 * * * /opt/tibet/stop_server.sh

0 13 * * * /opt/tibet/start_server.sh
50 15 * * * /opt/tibet/stop_server.sh

55 20 * * * /opt/tibet/start_server.sh
45 2 * * * /opt/tibet/stop_server.sh


