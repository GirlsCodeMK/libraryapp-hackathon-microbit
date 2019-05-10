import microbit

while True:
    text = input()
    microbit.display.scroll(text, loop=True, wait=False)
    