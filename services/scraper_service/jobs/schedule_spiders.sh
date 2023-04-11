#!/bin/bash

set -ex
echo "Scheduling spiders..."
cd /usr/project/news_scraper &&
    scrapyd-client schedule -p news_scraper tech-\*
