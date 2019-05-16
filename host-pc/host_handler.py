import serial
import asyncio
import serial_asyncio
import configparser
import random

config = configparser.ConfigParser()
with open('microbit.ini') as configfile:
    config.read(configfile)


port1 = '/dev/ttyACM0'
port2 = '/dev/ttyACM1'

try:
    ser = serial.Serial(port1, 115200, timeout=1, write_timeout=1)
except serial.serialutil.SerialException:
    ser = serial.Serial(port2, 115200, timeout=1, write_timeout=1)



# while True:
#     id = int(input('Enter destination ID: '))
#     if id == 0:
#         transmission = '\r\n'
#     else:
#         text = input('Enter message: ')
#         transmission = 'id:{};message:{}\r\n'.format(id, text)
#     ser.write(transmission.encode('utf-8'))
#     print('Wrote:', transmission)



async def serial_creator():
    return await serial_asyncio.open_serial_connection(url=port1, baudrate=115200)


async def keyboard_input(queue):
    while True:
        id = int(input('Enter destination ID: '))
        text = input('Enter message: ')
        transmission = f'id:{id};message:{text}'
        await queue.put(transmission)
        print(f'Enqueued {transmission}')

async def generate_messages(queue):
    for msg in [
                # {'id': 1, 'message': 'tom'}, 
                {'id': 2, 'message': 'alice'},
                # {'id': 1, 'message': 'dick'},
                # {'id': 2, 'message': 'bea'},
                # {'id': 1, 'message': 'harry'},
                # {'id': 2, 'message': 'claire'},
                # {'id': 1, 'message': 'john'},
                ]:
        await asyncio.sleep(3 + random.random())
        transmission = f"id:{msg['id']};message:{msg['message']}"
        await queue.put(transmission)
        print(f'Enqueued {transmission}')



async def serial_writer(queue, writer):
    print('Writer created')
    while True:
        try:
            message = queue.get_nowait()
        except asyncio.QueueEmpty:
            message = ''
        print(f'Serial write {message}')
        written = message + '\r\n'
        writer.write(written.encode('utf-8'))
        if message != '':
            queue.task_done()
        await asyncio.sleep(1.5)


async def serial_reader(reader):
    print('Reader created')
    while True:
        #msg = await reader.readuntil(b'\n')
        msg = await reader.readline()
        print(f'Received raw {msg}')
        message = msg.decode('utf-8').strip()
        print(f'Received "{message}"')


async def serial_handler():
    reader, writer = await serial_creator()
    queue = asyncio.Queue()

    # producer = asyncio.create_task(keyboard_input(queue))
    # consumer = asyncio.create_task(serial_writer(queue, serial_writer))
    # monitor = asyncio.create_task(serial_reader(reader))

    # await asyncio.gather(keyboard_input(queue), 
    #     serial_writer(queue, serial_writer),
    #     serial_reader(serial_reader),
    #     )

    consumer = asyncio.ensure_future(serial_writer(queue, writer))
    # await keyboard_input(queue)
    # await generate_messages(queue)
    # await serial_reader(reader)

    await asyncio.gather(generate_messages(queue), serial_reader(reader) )

    await queue.join()
    consumer.cancel()

#     print('Reader created')
#     _, writer = await serial_asyncio.open_serial_connection(url='./writer', baudrate=115200)
#     print('Writer created')
#     messages = [b'foo\n', b'bar\n', b'baz\n', b'qux\n']
#     sent = send(writer, messages)
#     received = recv(reader)
#     await asyncio.wait([sent, received])


# async def send(w, msg):
#     w.write(msg)
#     print(f'sent: {msg.decode().rstrip()}')
#     await asyncio.sleep(0.5)


# async def recv(r):
#     while True:
#         msg = await r.readuntil(b'\n')
#         print(f'received: {msg.rstrip().decode()}')


# loop = asyncio.get_event_loop()
# loop.run_until_complete(main(loop))
# loop.close()

# asyncio.run(serial_handler)

event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(serial_handler())
finally:
    event_loop.close()
