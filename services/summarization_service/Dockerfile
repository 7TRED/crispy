FROM python:3.10  

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ENV RMQ_HOST=
ENV RMQ_PORT=
ENV RMQ_USER=guest
ENV RMQ_PASS=guest
ENV RMQ_QUEUE=
ENV RMQ_EXCHANGE=
ENV RMQ_ROUTING_KEY=

COPY . .

CMD [ "python", "./main.py" ]