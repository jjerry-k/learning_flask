#!/bin/bash
rm -rf ~/Disk/Private/flask_server/log.out
nohup flask run --host 0.0.0.0 --port 5000 > ~/Disk/Private/flask_server/log.out &
