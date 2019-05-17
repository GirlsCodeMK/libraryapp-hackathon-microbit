import radio
import microbit

ID = 11

radio.config(length=250, channel=12)

microbit.display.scroll(('Waiting ' + str(ID)), loop=True, wait=False)

radio.on()

old_message = ''

while True:
    rcvd = radio.receive()
    if rcvd:
        terms = rcvd.strip().split(';')
        pairs = [term.strip().split(':') for term in terms]
        received = {k.strip() : v.strip() for [k, v] in pairs}

        if int(received.get('id', 0)) == ID:
            if 'message' in received:
                if received['message'] != old_message:
                    microbit.display.scroll(received['message'], loop=True, wait=False)
                    old_message = received['message']
            microbit.sleep(100)
            radio.send('ack:{}'.format(ID))