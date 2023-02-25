import amqp from 'amqplib';
import { RMQPublisher } from './publisher';
import { RMQListener } from './listener';

export class RMQConnection {
    private static instance: RMQConnection;
    private connection: amqp.Connection | null = null;
    private channel: amqp.Channel | null = null;

    private constructor () {}

    public static getInstance (): RMQConnection {
        if (!RMQConnection.instance) {
            RMQConnection.instance = new RMQConnection();
        }

        return RMQConnection.instance;
    }

    public async connect (host: string = 'localhost', port: number = 5672, user: string = 'guest', password: string = 'guest', vhost: string = '/'): Promise<void> {
        if (!this.connection) {
            this.connection = await amqp.connect(`amqp://${user}:${password}@${host}:${port}/${vhost}`);
            this.channel = await this.connection.createChannel();
        }
        else{
            throw new Error('Connection is already established');
        }
        
    }
    public async createPublisher (): Promise<RMQPublisher> {
        if (!this.channel) {
            throw new Error('Connection is not established');
        }
        return new RMQPublisher(this.channel);
    }
    public async createListener (): Promise<RMQListener> {
        if(!this.channel){
            throw new Error('Connection is not established');
        }
        return new RMQListener(this.channel);
    }
    public async close (): Promise<void> {
        if (this.connection) {
            await this.channel?.close();
            this.channel = null;
            await this.connection.close();
            this.connection = null;
        }
    }
}
