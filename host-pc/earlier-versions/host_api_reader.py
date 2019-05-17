import serial
import asyncio
import serial_asyncio
import configparser
import random
import requests
import datetime
import re
import copy

config = configparser.ConfigParser()
config.read('microbit.ini')
auth_headers = {'Authorization': 'Token {}'.format(config['DEFAULT']['token'])}

lock = asyncio.Lock()
known_microbits = {}


def parse_datetime(dt):
    conformed_timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', dt)
    try:
        timestamp = datetime.datetime.strptime(conformed_timestamp, "%Y%m%dT%H%M%S.%f%z" )
    except ValueError:
        timestamp = datetime.datetime.strptime(conformed_timestamp, "%Y%m%dT%H%M%S%z" )
    return timestamp

async def find_microbits():
    global known_microbits
    found_items = {}

    response = requests.get(config['DEFAULT']['hostname'] + 'copies/')
    copies = response.json()['results']
    for c in copies:
        if c['microbit_id']:
            if c['last_microbit_update']:
                last_update = parse_datetime(c['last_microbit_update'])
            else:
                last_update = None
            found_items[c['url']] = {'microbit_id': c['microbit_id'], 
                'last_update': last_update}
    
    response = requests.get(config['DEFAULT']['hostname'] + 'usermicrobits/', 
        headers=auth_headers)
    users = response.json()['results']

    for u in users:
        if u['microbit_id']:
            if u['last_microbit_update']:
                last_update = parse_datetime(u['last_microbit_update'])
            else:
                last_update = None
            found_items[u['url']] = {'microbit_id': u['microbit_id'], 
                'last_update': last_update}

    with await lock:
        known_microbits = copy.deepcopy(found_items)
        for mb in known_microbits:
            print('{}\t{}\t{}'.format(mb, 
                known_microbits[mb]['microbit_id'],
                known_microbits[mb]['last_update']))
        # print(known_microbits)


async def ping_microbits():
    global known_microbits
    with await lock:
        for mb in known_microbits:
            update_time = datetime.datetime.now(datetime.timezone.utc)
            response = requests.patch(mb, headers=auth_headers, 
                data={'last_microbit_update': update_time})
            print('Updated MB {} at {}, with response {}'.format(
                known_microbits[mb]['microbit_id'], mb, response.status_code))


async def find_microbits_loop():
    while True:
        await find_microbits()
        await asyncio.sleep(5)

async def ping_microbits_loop():
    while True:
        await ping_microbits()
        await asyncio.sleep(2)


async def api_handler():
    await asyncio.gather(
        ping_microbits_loop(),
        find_microbits_loop(),
        )



event_loop = asyncio.get_event_loop()
try:
    # event_loop.run_until_complete(find_microbits())
    # print(lock.locked())
    # print(known_microbits)
    event_loop.run_until_complete(api_handler())
    # event_loop.run_until_complete(ping_microbits())
finally:
    event_loop.close()
