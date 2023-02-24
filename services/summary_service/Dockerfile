FROM  node:18.14

WORKDIR /app

ENV MONGO_URI=

ADD package.json /app/package.json

RUN npm install 

ADD . /app

CMD [ "npm", "run", "dev" ]