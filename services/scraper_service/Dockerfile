FROM tred7/scrapyd:latest

ENV MONGO_URI=
ENV MONGO_DATABASE=

WORKDIR /usr/project/

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN \
    chmod 0644 schedule.cronjob \
    && crontab schedule.cronjob \
    && touch /var/log/cron.log

WORKDIR /usr/project/news_scraper

CMD scrapyd-deploy \
        && (cron -f &) \
        && tail -f /var/log/journal/scrapyd.service.log