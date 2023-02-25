import amqp from 'amqplib';

export class RMQPublisher {
    private channel: amqp.Channel;

    constructor (channel: amqp.Channel) {
        this.channel = channel;
    }
    public declareExchange (exchangeName: string, exchangeType: string = '', options: amqp.Options.AssertExchange = {}): Promise<amqp.Replies.AssertExchange> {
        return this.channel.assertExchange(exchangeName, exchangeType, options);
    }
    public declareQueue (queueName: string, options: amqp.Options.AssertQueue = {}): Promise<amqp.Replies.AssertQueue> {
        return this.channel.assertQueue(queueName, options);
    }
    public bindQueue (queueName: string, exchangeName: string, routingKey: string = '', args: any = {}): Promise<amqp.Replies.Empty> {
        return this.channel.bindQueue(queueName, exchangeName, routingKey, args);
    }
    public publish (exchangeName: string, routingKey: string, content: Buffer, options: amqp.Options.Publish = {}): boolean {
        return this.channel.publish(exchangeName, routingKey, content, options);
    }
}
