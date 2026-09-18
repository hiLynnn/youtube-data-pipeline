#!/bin/bash

cd /home/linh/Documents/youtube-data-pipeline

source .venv/bin/activate

python main.py >> logs/cron.log 2>&1 