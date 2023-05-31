FROM  node:18.14

WORKDIR /app

ENV MONGO_URI=""
ENV MONGO_DB=""

ADD package.json /app/package.json

RUN npm install && npm cache clean --force

ADD . /app

EXPOSE 3000

CMD npm run start:watch