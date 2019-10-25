#!/usr/bin/env bash


crontab -e

add following script lines.

55 8 * * *  /home/scott/geniusbar/start_server.sh
45 11 * * * /home/scott/geniusbar/stop_server.sh

0 13 * * * /home/scott/geniusbar/start_server.sh
50 15 * * * /home/scott/geniusbar/stop_server.sh

55 20 * * * /home/scott/geniusbar/start_server.sh
45 2 * * * /home/scott/geniusbar/stop_server.sh


50 15 * * * /home/scott/geniusbar/start_server.sh
45 2 * * * /home/scott/geniusbar/stop_server.sh

