import amqp from 'amqplib';
import { RMQPublisher } from './publisher';
import { RMQListener } from './listener';

export class RMQConnection {
    private static instance: RMQConnection;
    private connection: amqp.Connection | null = null;
    private channel: amqp.Channel | null = null;
    private static MAX_RETRIES = 10;
    private static RETRY_INTERVAL = 5000;
    private constructor () {}

    public static getInstance (): RMQConnection {
        if (!RMQConnection.instance) {
            RMQConnection.instance = new RMQConnection();
        }

        return RMQConnection.instance;
    }

    public async connect (
        host: string = 'localhost',
        port: number = 5672,
        user: string = 'guest',
        password: string = 'guest',
        vhost: string = '/',
        retryInterval: number = RMQConnection.RETRY_INTERVAL, // retry interval in milliseconds
        maxRetries: number = RMQConnection.MAX_RETRIES // maximum number of retries
    ): Promise<void> {
        let retries = 0;
        while (!this.connection && retries < maxRetries) {
            try {
                this.connection = await amqp.connect(`amqp://${user}:${password}@${host}:${port}/${vhost}`);
                this.channel = await this.connection.createChannel();
            } catch (err) {
                console.error(`Failed to connect to RabbitMQ server: ${err.message}`);
                this.connection = null;
                this.channel = null;
                retries++;
                if (retries < maxRetries) {
                    console.log(`Retrying connection to RabbitMQ server in ${retryInterval / 1000} seconds...`);
                    await new Promise(resolve => setTimeout(resolve, retryInterval));
                }
            }
        }
        if (!this.connection) {
            throw new Error(`Failed to connect to RabbitMQ server after ${maxRetries} attempts`);
        }
    }

    public async createPublisher (): Promise<RMQPublisher> {
        if (!this.channel) {
            throw new Error('No connection available to create a publisher');
        }
        return new RMQPublisher(this.channel);
    }

    public async createListener (): Promise<RMQListener> {
        if (!this.channel) {
            throw new Error('No connection available to create a listener');
        }
        return new RMQListener(this.channel);
    }

    public async close (): Promise<void> {
        try {
            if (this.channel) {
                await this.channel.close();
                this.channel = null;
            }
            if (this.connection) {
                await this.connection.close();
                this.connection = null;
            }
        } catch (err) {
            console.error(`Failed to close connection to RabbitMQ server: ${err.message}`);
            throw err;
        }
    }
}
