import serial

port = '/dev/ttyACM0'

ser = serial.Serial(port, 115200, timeout=1, write_timeout=1)

while True:
    text = input('Enter message: ')
    ser.write((text + '\r\n').encode('utf-8'))
