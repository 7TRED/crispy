FROM python:3.10  

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ENV RMQ_HOST=
ENV RMQ_PORT=
ENV RMQ_USER=guest
ENV RMQ_PASS=guest
ENV MONGO_URI=
ENV MONGO_DB=

COPY . .

CMD [ "python", "-m", "summarizer" ]