import serial
import asyncio
import requests
import json
from configparser import SafeConfigParser

serial_path = '/dev/ttyUSB3'
serial_baudrate = 115200


def read_config():
    config = SafeConfigParser()
    config.read('config.ini')
    return config.get('REST API', 'host')


def read(host):
    ser = serial.Serial(serial_path, serial_baudrate)

    while True:
        line = ser.readline().decode('ascii')
        split_line = line.split()
        print(line)
        if split_line[0] == "Sensor:":
            try:
                mote_id = int(split_line[1])
                temperature = float(split_line[2])
                humidity = float(split_line[3])
            except ValueError:
                print("Error")
            else:
                print("ID: " + split_line[1] + "\tTemperature: " + split_line[2] + "\tHumidity: " + split_line[3])

            send_request(host, mote_id, timestamp, temperature, humidity)


async def send_request(host, mote_id, timestamp, temperature, humidity):
    response = requests.put(
        host + '/addMeasurement',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'moteId': str(mote_id),
            'timestamp': str(timestamp * 1000),
            'temperature': str(temperature),
            'humidity': str(humidity)
        }))
    print(response)


def start():
    host = read_config()
    read(host)


start()
