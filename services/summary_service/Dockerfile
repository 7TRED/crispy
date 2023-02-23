FROM  node:18.14

WORKDIR /app

ENV MONGO_URI=

COPY . .

RUN npm install 

CMD [ "npm", "run", "dev" ]