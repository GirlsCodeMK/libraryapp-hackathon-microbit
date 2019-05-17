import serial
import asyncio
import serial_asyncio
import configparser
import random
import aiohttp
import datetime
import re
import copy

config = configparser.ConfigParser()
config.read('microbit.ini')
auth_headers = {'Authorization': 'Token {}'.format(config['DEFAULT']['token'])}

port1 = '/dev/ttyACM0'


lock = asyncio.Lock()
known_microbits = {}


def parse_datetime(dt):
    """Deal with the strange formatting of timezones"""
    conformed_timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', dt)
    try:
        timestamp = datetime.datetime.strptime(conformed_timestamp, "%Y%m%dT%H%M%S.%f%z" )
    except ValueError:
        timestamp = datetime.datetime.strptime(conformed_timestamp, "%Y%m%dT%H%M%S%z" )
    return timestamp


async def serial_creator():
    """Open the connection to the connected microbit"""
    return await serial_asyncio.open_serial_connection(url=port1, baudrate=115200)



async def find_microbits(session):
    """Find all the microbits known in the api and create a new version of 
    `known_microbits` that stsores them."""
    global known_microbits
    found_items = {}

    async with session.get(config['DEFAULT']['hostname'] + 'copies/') as response:
        respj = await response.json()
        copies = respj['results']
        for c in copies:
            if c['microbit_id']:
                if c['last_microbit_update']:
                    last_update = parse_datetime(c['last_microbit_update'])
                else:
                    last_update = None
                if c['on_loan']:
                    message = 'On loan'
                else:
                    message = 'Available'
                found_items[c['url']] = {'microbit_id': c['microbit_id'], 
                    'last_update': last_update,
                    'message': message,
                    }
    

    async with session.get(config['DEFAULT']['hostname'] + 'usermicrobits/', 
        headers=auth_headers) as response:
        respj = await response.json()
        users = respj['results']

        for u in users:
            if u['microbit_id']:
                if u['last_microbit_update']:
                    last_update = parse_datetime(u['last_microbit_update'])
                else:
                    last_update = None
                found_items[u['url']] = {'microbit_id': u['microbit_id'], 
                    'last_update': last_update,
                    'message': 'User ' + str(u['microbit_id'])}

    with await lock:
        known_microbits = copy.deepcopy(found_items)
        for mb in known_microbits:
            print('{}\t{}\t{}'.format(mb, 
                known_microbits[mb]['microbit_id'],
                known_microbits[mb]['last_update']))
        # print(known_microbits)


async def generate_messages(queue):
    while True:
        with await lock:
            for mb in known_microbits:
                id = known_microbits[mb]['microbit_id']
                msg = known_microbits[mb]['message']
                transmission = f"id:{id};message:{msg}"
                await queue.put(transmission)
                print(f'Enqueued {transmission}')
        await asyncio.sleep(1.0)


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
        await asyncio.sleep(0.5)


async def serial_reader(reader, session):
    print('Reader created')
    while True:
        #msg = await reader.readuntil(b'\n')
        msg = await reader.readline()
        message = msg.decode('utf-8').strip()
        print(f'Received {message}')
        if message.startswith('ack:'):
            responding_microbit_id = int(message.split(':')[1].strip())
            with await lock:
                for mb in known_microbits:
                    if known_microbits[mb]['microbit_id'] == responding_microbit_id:
                        update_time = datetime.datetime.now(datetime.timezone.utc)
                        async with session.patch(mb, 
                                headers=auth_headers, 
                                data={'last_microbit_update': update_time}
                                ) as response:
                            print('Updated MB {} at {}, with response {}'.format(
                                known_microbits[mb]['microbit_id'], mb, 
                                response.status))




# async def ping_microbits(session):
#     """Update the status of a microbit after it's returned a radio message"""
#     with await lock:
#         for mb in known_microbits:
#             update_time = datetime.datetime.now(datetime.timezone.utc)
#             async with session.patch(mb, 
#                     headers=auth_headers, 
#                     data={'last_microbit_update': update_time}) as response:
#                 print('Updated MB {} at {}, with response {}'.format(
#                     known_microbits[mb]['microbit_id'], mb, response.status))


async def find_microbits_loop(session):
    while True:
        await find_microbits(session)
        await asyncio.sleep(5)

# async def ping_microbits_loop(session):
#     while True:
#         await ping_microbits(session)
#         await asyncio.sleep(2)


async def api_handler():
    reader, writer = await serial_creator()
    queue = asyncio.Queue(maxsize=5)

    async with aiohttp.ClientSession() as session:
        consumer = asyncio.ensure_future(serial_writer(queue, writer))
        await asyncio.gather(
            generate_messages(queue), 
            serial_reader(reader, session),
            find_microbits_loop(session),
            )
        await queue.join()
        consumer.cancel()




event_loop = asyncio.get_event_loop()
try:
    # event_loop.run_until_complete(find_microbits())
    # print(lock.locked())
    # print(known_microbits)
    event_loop.run_until_complete(api_handler())
    # event_loop.run_until_complete(ping_microbits())
finally:
    event_loop.close()
