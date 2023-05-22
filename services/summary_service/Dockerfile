FROM  node:18.14

WORKDIR /app

ENV MONGO_URI=""

ADD package.json /app/package.json

RUN npm install && npm cache clean --force

ADD . /app

EXPOSE 3000

RUN npm run build

CMD npm run start:watch