#!/bin/bash

set -ex

cd /usr/project/news_scraper

scrapyd-deploy

cd /usr/project

if [ -z "$MODE"]; then
    echo "MODE not set, assuming Development"
    MODE="Development"
fi

CRON_FILE="crontab.$MODE"

echo "Loading crontab from $CRON_FILE"

crontab $CRON_FILE

echo "Starting cron"

cron -f