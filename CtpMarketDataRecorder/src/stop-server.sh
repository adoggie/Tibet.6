#!/usr/bin/env bash

ps -eaf | grep server-data- | awk '{print $2}' | xargs kill -9 {}
