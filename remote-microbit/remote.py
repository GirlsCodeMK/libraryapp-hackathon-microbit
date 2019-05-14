import radio
import microbit

ID = 1

microbit.display.scroll(('Waiting ' + str(ID)), loop=True, wait=False)

radio.on()

while True:
    rcvd = radio.receive()
    if rcvd:
        received = {k.strip(): v.strip() for [k, v] in [term.strip().split(':') for term in rcvd.split(';')]}

        if int(received.get('id', 0)) == ID:
            if 'message' in received:
                microbit.display.scroll(received['message'], loop=True, wait=False)
                microbit.sleep(100)
                radio.send('ack {}'.format(ID))