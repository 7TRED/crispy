FROM  node:18.14

WORKDIR /app

ENV MONGO_URI=

COPY . /app

RUN npm install 

CMD [ "npm", "run", "dev" ]