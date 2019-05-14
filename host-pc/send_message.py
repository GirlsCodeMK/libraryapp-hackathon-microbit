import serial

port1 = '/dev/ttyACM0'
port2 = '/dev/ttyACM1'

try:
    ser = serial.Serial(port1, 115200, timeout=1, write_timeout=1)
except serial.serialutil.SerialException:
    ser = serial.Serial(port2, 115200, timeout=1, write_timeout=1)


while True:
    id = int(input('Enter destination ID: '))
    if id == 0:
        transmission = '\r\n'
    else:
        text = input('Enter message: ')
        transmission = 'id:{};message:{}\r\n'.format(id, text)
    ser.write(transmission.encode('utf-8'))
    print('Wrote:', transmission)
