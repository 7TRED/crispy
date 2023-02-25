import amqp from 'amqplib';

export class RMQListener {
    constructor (private channel: amqp.Channel) {
        //constructor for RMQListener
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
    public consume (queueName: string, callback: (msg: amqp.ConsumeMessage | null) => void, options: amqp.Options.Consume = {}): Promise<amqp.Replies.Consume> {
        return this.channel.consume(queueName, callback, options);
    }
}
