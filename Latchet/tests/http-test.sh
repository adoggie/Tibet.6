#!/usr/bin/env bash

curl -l -H "Content-type: application/json" -X POST -d '["a","b","c"]' http://127.0.0.1:18901/v1/contract/subscribe
curl -l  http://127.0.0.1:18901/v1/contract/list

