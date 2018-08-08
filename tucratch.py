#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import webbrowser
import serial
import serial.tools.list_ports
import json
from flask import Flask, render_template, request, redirect, make_response
from time import sleep
import time
import threading
import re

'''------Global values------'''

serial_cache = ""
serial_lock = 0

datas = {
    "knob_value": "0",
    "knob_button": "0",
    "environment_temp": "0",
    "environment_humid": "0",
    "environment_pascal": "0",
    "environment_light": "0",
    "environment_2_temp": "0",
    "environment_2_humid": "0",
    "environment_2_pascal": "0",
    "environment_2_light": "0",
    "co2sensor_value": "0",
    "phsensor_value": "0",
    "distance": "0"
}

serialnums = {
    "led": "1001",
    "knob": "1007",
    "environment": "1003",
    "distance": "100a",
    "motor": "1005",
    "phsensor": "1008",
    "co2sensor": "1009"
}

ids = {
    "led": [],
    "knob": [],
    "environment": [],
    "distance": [],
    "motor": [],
    "phsensor": [],
    "co2sensor": []
}

'''------Functions------'''


def serial_ports():
    ports = serial.tools.list_ports.comports()
    port_list = []
    for port in ports:
        port_list.append(port.device)
    return port_list

def serial_conversation(transmit_data):
    global serial_cache
    global serial_lock
    i = 0
    while serial_lock > 0:
        sleep(0.001)
        i += 1
        if i > 1000:
            print "#### Serial is busy. ####"
            return
    serial_lock = 1
    while ser.in_waiting > 0:
        sleep(0.02)
    print "## Serial conversation start. ##"
    print ">> " + transmit_data
    ser.write(transmit_data)
    while ser.out_waiting > 0:
        sleep(0.001)
    print "## Serial conversation end. ##"
    serial_lock = 0

def serial_parse():
    global serial_cache
    while True:
        sleep(0.01)
        #print "## Serial reading ##"
        if ser.in_waiting > 0:
            bStr = ser.read(128);
            for c in bStr:
                if c == b'\x0a':
                    print "<< " + serial_cache
                    try:
                        response = json.loads(serial_cache)
                        serial_cache = ""
                    except:
                        print "#### JSON parse error! ####"
                        serial_cache = ""
                        continue
                    respons_parse(response)
                elif c < b'~' and c > b'!':
                    serial_cache += c[0]

def respons_parse(input):
    global datas
    global ids
    global serialnums

    #print input

    if 'bridge' in input:
        devices = input['bridge']
        ids = {
            "led": [],
            "knob": [],
            "environment": [],
            "distance": [],
            "motor": [],
            "phsensor": [],
            "co2sensor": []
        }
        for device in devices:
            if re.compile(serialnums["led"]).match(device):
                ids['led'].append(device);
            if re.compile(serialnums["environment"]).match(device):
                ids['environment'].append(device)
            if re.compile(serialnums["motor"]).match(device):
                ids['motor'].append(device)
            if re.compile(serialnums["knob"]).match(device):
                ids['knob'].append(device)
            if re.compile(serialnums["distance"]).match(device):
                ids['distance'].append(device)
            if re.compile(serialnums["co2sensor"]).match(device):
                ids['co2sensor'].append(device)
            if re.compile(serialnums["phsensor"]).match(device):
                ids['phsensor'].append(device)
        print ids
    elif input['status'] == 200:
        id = input['id']
        port = input['port']
        if len(ids["distance"]) > 0 and re.compile(ids["distance"][0]).match(id):
            if port == 1:
                datas['distance'] = str(input.get('data'))
        elif len(ids["knob"]) > 0 and re.compile(ids["knob"][0]).match(id):
            if port == 1:
                datas['knob_value'] = str(input.get('data'))
            elif port == 2:
                datas['knob_button'] = str(input.get('data'))
        elif len(ids["environment"]) > 0 and re.compile(ids["environment"][0]).match(id):
            if port == 1:
                datas['environment_temp'] = str(input.get('data'))
            elif port == 2:
                datas['environment_humid'] = str(input.get('data'))
            elif port == 3:
                datas['environment_pascal'] = str(input.get('data'))
            elif port == 4:
                datas['environment_light'] = str(input.get('data'))
        elif len(ids["environment"]) > 1 and re.compile(ids["environment"][1]).match(id):
            if port == 1:
                datas['environment_2_temp'] = str(input.get('data'))
            elif port == 2:
                datas['environment_2_humid'] = str(input.get('data'))
            elif port == 3:
                datas['environment_2_pascal'] = str(input.get('data'))
            elif port == 4:
                datas['environment_2_light'] = str(input.get('data'))
        elif len(ids["co2sensor"]) > 0 and re.compile(ids["co2sensor"][0]).match(id):
            if port == 1:
                datas['co2sensor_value'] = str(input.get('data'))
        elif len(ids["phsensor"]) > 0 and re.compile(ids["phsensor"][0]).match(id):
            if port == 1:
                datas['phsensor_value'] = str(input.get('data'))


'''-----Main Activity-----'''

webbrowser.open('http://127.0.0.1:8081/')

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

serialThread = threading.Thread(target=serial_parse)

'''-----Web UI-----'''


@app.route('/', methods=['GET'])
def index():
    if 'ser' in globals():
        if ser.is_open:
            status = 'ConnectingSuccess!'
    else:
        status = ''
    return render_template('index.html', ports=serial_ports(), status=status)


'''-----Scratch Comander-----'''
# Polling
@app.route('/poll', methods=['GET'])
def res():
    global datas
    responce = 'knob_value_data ' + datas["knob_value"] + '\n' + \
               'knob_button_data ' + datas["knob_button"] + '\n' + \
               'environment_temp_data ' + datas["environment_temp"] + '\n' + \
               'environment_humid_data ' + datas["environment_humid"] + '\n' + \
               'environment_pascal_data ' + datas["environment_pascal"] + '\n' + \
               'environment_light_data ' + datas["environment_light"] + '\n'+ \
               'environment_2_temp_data ' + datas["environment_2_temp"] + '\n' + \
               'environment_2_humid_data ' + datas["environment_2_humid"] + '\n' + \
               'environment_2_pascal_data ' + datas["environment_2_pascal"] + '\n' + \
               'environment_2_light_data ' + datas["environment_2_light"] + '\n'+ \
               'distance_data ' + datas["distance"] + '\n' + \
               'co2sensor_value_data ' + datas["co2sensor_value"] + '\n' + \
               'phsensor_value_data ' + datas["phsensor_value"] + '\n'

    value = str(responce)
    resp = make_response(value)
    resp.headers['Content-Type'] = 'text/plain'
    return resp


# Reset & init
@app.route('/reset_all', methods=['GET'])
def reset_all():
    global serial_cache
    serial_cache = ""
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    command = "/\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


# LEDs
@app.route('/led_red/<id>/<data>', methods=['GET'])
def led_red(id, data):
    global ids
    command = ids['led'][0] + "/1" + " " + str(data) + "\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

@app.route('/led_green/<id>/<data>', methods=['GET'])
def led_green(id, data):
    global ids
    command = ids['led'][0] + "/2" + " " + str(data) + "\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

@app.route('/led_blue/<id>/<data>', methods=['GET'])
def led_blue(id, data):
    global ids
    command = ids['led'][0] + "/3" + " " + str(data) + "\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

@app.route('/led_all/<id>/<red>/<green>/<blue>', methods=['GET'])
def led_all(id, red, green, blue):
    global ids
    command = ids["led"][0] + "/1 " + str(red) + "\n" + \
              ids["led"][0] + "/2 " + str(green) + "\n" + \
              ids["led"][0] + "/3 " + str(blue) + "\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


# Knob
@app.route('/knob_value/<id>', methods=['GET'])
def knob_value(id):
    global ids
    command = ids["knob"][0] + "/1\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

@app.route('/knob_button/<id>', methods=['GET'])
def knob_button(id):
    global ids
    command = ids["knob"][0] + "/2\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

@app.route('/knob_reset/<id>', methods=['GET'])
def knob_reset(id):
    global ids
    command = ids["knob"][0] + "/1 0\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

## Knob LED (red)
@app.route('/knob_led_red/<id>/<data>', methods=['GET'])
def knob_led_red(id, data):
    global ids
    command = ids['knob'][0] + "/4" + " " + str(data) + "\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

## Knob LED (green)
@app.route('/knob_led_green/<id>/<data>', methods=['GET'])
def knob_led_green(id, data):
    global ids
    command = ids['knob'][0] + "/5" + " " + str(data) + "\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

## Knob LED (blue)
@app.route('/knob_led_blue/<id>/<data>', methods=['GET'])
def knob_led_blue(id, data):
    global ids
    command = ids['knob'][0] + "/6" + " " + str(data) + "\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

## Knob LEDs (rgb)
@app.route('/knob_led_all/<id>/<red>/<green>/<blue>', methods=['GET'])
def knob_led_all(id, red, green, blue):
    global ids
    command = ids["knob"][0] + "/4 " + str(red) + "\n" + \
              ids["knob"][0] + "/5 " + str(green) + "\n" + \
              ids["knob"][0] + "/6 " + str(blue) + "\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

# Environment sensor
## temp
@app.route('/environment_temp/<id>', methods=['GET'])
def environment_temp(id):
    global ids
    command = ids["environment"][0] + "/1\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

## humid
@app.route('/environment_humid/<id>', methods=['GET'])
def environment_humid(id):
    global ids
    command = ids["environment"][0] + "/2\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

## pressure
@app.route('/environment_pascal/<id>', methods=['GET'])
def environment_pascal(id):
    global ids
    command = ids["environment"][0] + "/3\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

## light
@app.route('/environment_light/<id>', methods=['GET'])
def environment_light(id):
    global ids
    command = ids["environment"][0] + "/4\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


# Environment sensor (multiple)
## Temperature
@app.route('/environment_temp/<id>/<num>', methods=['GET'])
def environment_multiple_temp(id, num):
    global ids
    command = ids["environment"][int(num) - 1] + "/1\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

## Humid
@app.route('/environment_humid/<id>/<num>', methods=['GET'])
def environment_multiple_humid(id, num):
    global ids
    command = ids["environment"][int(num) - 1] + "/2\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

## Pressure
@app.route('/environment_pascal/<id>/<num>', methods=['GET'])
def environment_multiple_pascal(id, num):
    global ids
    command = ids["environment"][int(num) - 1] + "/3\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

## Luxmeter
@app.route('/environment_light/<id>/<num>', methods=['GET'])
def environment_multiple_light(id, num):
    global ids
    command = ids["environment"][int(num) - 1] + "/4\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


# Distance meter
@app.route('/distance/<id>', methods=['GET'])
def distance(id):
    global ids
    command = ids["distance"][0] + "/1\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


# DC motor
@app.route('/motor_rotate/<id>/<data>', methods=['GET'])
def motor_rotate(id, data):
    global ids
    command = ids["motor"][0] + "/1 " + str(data) + "\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

@app.route('/motor_stop/<id>', methods=['GET'])
def motor_stop(id):
    global ids
    command = ids["motor"][0] + "/1 0\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


# DC motor (multiple)
@app.route('/motor_rotate/<id>/<num>/<value>', methods=['GET'])
def motor_multiple_rotate(id, num, value):
    global ids
    command = ids["motor"][int(num) - 1] + "/1 " + str(data) + "\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

@app.route('/motor_stop/<id>/<num>', methods=['GET'])
def motor_multiple_stop(id, num):
    global ids
    command = ids["motor"][int(num) - 1] + "/1 0\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


# pH sensor
@app.route('/phsensor_value/<id>', methods=['GET'])
def phsensor_value(id):
    global ids
    command = ids["phsensor"][0] + "/1\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


# CO2 sensor
@app.route('/co2sensor_value/<id>', methods=['GET'])
def co2sensor_value(id):
    global ids
    command = ids["co2sensor"][0] + "/1\n"
    serial_conversation(command.encode())
    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


'''-----Web APIs-----'''

@app.route('/api/postport', methods=['POST'])
def postport():
    global serialThread
    port = request.form.get('port-selector')
    if 'ser' in globals():
        ser.close()
    else:
        global ser
        ser = serial.Serial(port, 9600,  timeout=0)
        serialThread.start()
    return redirect("http://127.0.0.1:8081/", code=302)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)
