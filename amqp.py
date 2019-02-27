import asyncio
import aio_pika
import orm
import json
import signal

queue_name = "test_queue1"


async def get_messages(channel):
    # Declaring queue
    queue = await channel.declare_queue(
        queue_name,
        auto_delete=True
    )   # type: aio_pika.Queue
    async with queue.iterator() as queue_iter:
        # Cancel consuming after __aexit__
        async for message in queue_iter:
            async with message.process():
                data = json.loads(message.body)
                user = await orm.task(data)
                print(f'saved user {user}')


async def call(channel):
    queue = await channel.declare_queue(
        queue_name,
        auto_delete=True
    )   # type: aio_pika.Queue

    print("sending messages")

    body = json.dumps({
        'nickname': 'kaspa'
    })

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=body.encode()
        ),
        routing_key=queue_name
    )


async def main():
    await orm.setup()

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/", loop=asyncio.get_event_loop()
    )

    async with connection:
        print("amqp connected")

        # Creating channel
        channel = await connection.channel()    # type: aio_pika.Channel

        await asyncio.gather(
            get_messages(channel),
            call(channel),
        )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    def my_handler():
        print('Stopping')
        for task in asyncio.Task.all_tasks():
            task.cancel()
        loop.stop()

    loop.add_signal_handler(signal.SIGINT, my_handler)
    asyncio.ensure_future(main())
    loop.run_forever()
