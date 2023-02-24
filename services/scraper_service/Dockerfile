FROM tred7/scrapyd:latest

RUN set -ex \
    && apt-get update \
    && apt-get install -y dos2unix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV MONGO_URI=
ENV MONGO_DATABASE=
ENV MODE=
ENV RMQ_HOST=
ENV RMQ_PORT=
ENV RMQ_QUEUE=
ENV RMQ_EXCHANGE=
ENV RMQ_ROUTING_KEY=

WORKDIR /usr/project/

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN dos2unix crontab.* *.sh jobs/*.* \
    && \
    find . -type f -iname "*.sh" -exec chmod +x {} \; \
    && find . -type f -iname "crontab.*" -exec chmod 0644 {} \; \
    && touch /var/log/cron.log

CMD ["./start.sh"]