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
        # received = {k.strip(): v.strip() for [k, v] in [term.strip().split(':') for term in rcvd.split(';')]}
        # microbit.display.scroll(rcvd.strip(), loop=True, wait=False)
        terms = rcvd.strip().split(';')
        # microbit.display.scroll('*'.join(terms), loop=True, wait=False)

        pairs = [term.strip().split(':') for term in terms]
        received = {k.strip() : v.strip() for [k, v] in pairs}
        # microbit.display.scroll('*'.join(received.values()), loop=True, wait=False)

        if int(received.get('id', 0)) == ID:
            if 'message' in received:
                if received['message'] != old_message:
                    microbit.display.scroll(received['message'], loop=True, wait=False)
                    old_message = received['message']
            microbit.sleep(100)
            radio.send('ack:{}'.format(ID))