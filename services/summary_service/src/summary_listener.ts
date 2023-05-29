import { Channel, Connection, ConsumeMessage, connect } from "amqplib";
import * as mongoDB from "mongodb";

interface SummaryListenerConfig {
  RabbitMQUrl: string;
  Queue: string;
  MongoDBConnString: string;
  MongoDBDatabase: string;
  MongoDBCollection: string;
}

let config: SummaryListenerConfig = {
  RabbitMQUrl: "amqp://username:password@localhost:5672",
  MongoDBConnString:
    "mongodb+srv://ghost:tangoChar1+@ghostcluster.hkc8jmw.mongodb.net/?retryWrites=true&w=majority",
  Queue: "testQueue",
  MongoDBDatabase: "crispy",
  MongoDBCollection: "summarized_articles",
};

const writeToCollection = async (
  data: string,
  collection: mongoDB.Collection
) => {
  console.log(`Written to DB: ${data}`);

  await collection.insertOne(JSON.parse(data));
};

async function consumer(channel: Channel, collection: mongoDB.Collection) {
  return async (msg: ConsumeMessage | null) => {
    if (msg) {
      // Display the received message
      // Acknowledge the message
      let data = Buffer.from(msg.content).toString();
      console.log(data);
      await writeToCollection(data, collection);
      channel.ack(msg);
    }
  };
}

const getArticle = () => {
  return {
    title: "A new malware in market",
    url: "https://url.com",
    content: "asdfasdfasdasdfasdf",
    date: "20/05/2023",
  };
};

async function sendMessages() {
  const connection: Connection = await connect(config.RabbitMQUrl);

  // Create a channel
  const channel: Channel = await connection.createChannel();

  // Makes the queue available to the client
  await channel.assertQueue(config.Queue);

  //Send a message to the queue

  channel.sendToQueue(config.Queue, Buffer.from(JSON.stringify(getArticle())));
}

async function connectToDatabase() {
  let client: mongoDB.MongoClient = new mongoDB.MongoClient(
    config.MongoDBConnString,
    {
      serverApi: {
        version: mongoDB.ServerApiVersion.v1,
        strict: true,
        deprecationErrors: true,
      },
    }
  );
  try {
    await client.connect();
  } catch (e) {
    throw e;
  }

  const db: mongoDB.Db = client.db(config.MongoDBDatabase);

  return db;
}

async function summaryListener() {
  const connection: Connection = await connect(config.RabbitMQUrl);

  const channel: Channel = await connection.createChannel();
  channel.assertQueue(config.Queue);

  let db: mongoDB.Db;
  try {
    db = await connectToDatabase();
  } catch (e) {
    throw e;
  }

  let collection: mongoDB.Collection = await db.collection(
    config.MongoDBCollection
  );

  await channel.consume(config.Queue, await consumer(channel, collection));
}

// Main
(async () => {
  await sendMessages();

  try {
    await summaryListener();
  } catch (e) {
    console.log(e);
  }
})();
