import serial
import logging
import asyncio
import requests
import json
import sys
import time
from configparser import SafeConfigParser

serial_path = '/dev/ttyUSB0'
host = 'http://localhost:3000'
sandbox = False
debug = False

if len(sys.argv) > 1:
    serial_path = sys.argv[1]
serial_baudrate = 115200


def read_config():
    global host
    global sandbox
    global serial_path
    global debug

    config = SafeConfigParser()

    config.read('config.ini')
    serial_path = config.get('REST API', 'serial_path',
                             fallback='/dev/ttyUSB0')
    host = config.get('REST API', 'host', fallback='http://localhost:3000')
    sandbox = config.getboolean('REST API', 'sandbox', fallback=False)
    debug = config.getboolean('REST API', 'debug', fallback=False)


def read():
    ser = serial.Serial(serial_path, serial_baudrate)

    while True:
        line = ser.readline().decode('ascii')
        split_line = line.split()
        if split_line[0] == "Sensor:":
            try:
                timestamp = time.time()
                msg_id = int(split_line[1])
                mote_id = int(split_line[2])
                temperature = float(split_line[3])
                humidity = float(split_line[4])
                if debug:
                    print("Message ID: {}\tMote ID: {}\tTemperature: {}\tHumidity: {}".format(
                        msg_id, mote_id, temperature, humidity))

                if not sandbox:
                    send_request(host, timestamp, mote_id,
                                 temperature, humidity)
            except ValueError:
                print("Error")


def send_request(host, timestamp, mote_id, temperature, humidity):
    response = requests.put(
        host + '/addMeasurement',
        headers={'content-type': 'application/json'},
        data=json.dumps({
            'moteId': str(mote_id),
            'timestamp': str(timestamp * 1000),
            'temperature': str(temperature),
            'humidity': str(humidity)
        }))


def start():
    read_config()
    logging.basicConfig(filename="log.log", level=logging.DEBUG)
    while True:
        try:
            read()
        except Exception as e:
            logging.exception(e)


start()
