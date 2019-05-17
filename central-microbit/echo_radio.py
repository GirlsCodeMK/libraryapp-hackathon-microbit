import radio
import microbit

radio.config(length=250, channel=12)

radio.on()
radio.send('Ready')

microbit.display.scroll("Send wait", loop=True, wait=False)

while True:
    text = input()
    if text:
        last_text = text
        radio.send(text)
        microbit.display.scroll(text, loop=True, wait=False)
    response = radio.receive()
    if response:
        microbit.display.scroll(last_text + ' <- ' + response, loop=True, wait=False)
        # print(''.join(reversed(response)))
        print(response.strip())