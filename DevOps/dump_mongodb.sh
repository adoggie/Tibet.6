#!/usr/bin/env bash

#mongodump  -u  superuser -p 123456 --port 27017  --authenticationDatabase admin -d myTest -o  /backup/mongodb/
mongodump   -d Ctp_Tick -o  /backup/mongodb/