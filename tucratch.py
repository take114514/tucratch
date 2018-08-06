#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import webbrowser
import serial
import serial.tools.list_ports
import json
from flask import Flask, render_template, request, redirect, make_response
from time import sleep
import re

'''------Global values------'''

serial_cache = ""

datas = {
    "knob": "0",
    "knobbutton": "0",
    "temp": "0",
    "humid": "0",
    "pascal": "0",
    "light": "0",
    "distance": "0"
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
    ser.write(transmit_data)

    while ser.out_waiting > 0:
        sleep(0.001)

    wait_count = 0

    while True:
        if ser.in_waiting > 0:
            wait_count = 0
            c = ser.read(1);
            if len(c) == 0:
                break
            elif c[0] == b'\x0a':
                try:
                    respons_parse(json.loads(serial_cache))
                    serial_cache = ""
                except:
                    print "### JSON parse error! ###"
                    print serial_cache
                    serial_cache = ""
            elif c[0] < b'~' and c[0] > b'!':
                serial_cache += c[0]
        elif ser.in_waiting == 0:
            sleep(0.001)
            wait_count += 1
            if wait_count > 10:
                break

def respons_parse(input):
    global datas
    if input['status'] == 200:
        id = input['id']
        port = input['port']
        print input
        if re.compile("100a-").search(id) and port == 1:
            datas['distance'] = str(input.get('data'))
        if re.compile("1007-").search(id) and port == 1:
            datas['knob'] = str(input.get('data'))
        if re.compile("1007-").search(id) and port == 2:
            datas['knobbutton'] = str(input.get('data'))
        if re.compile("1003-").search(id) and port == 1:
            datas['temp'] = str(input.get('data'))
        if re.compile("1003-").search(id) and port == 2:
            datas['humid'] = str(input.get('data'))
        if re.compile("1003-").search(id) and port == 3:
            datas['pascal'] = str(input.get('data'))
        if re.compile("1003-").search(id) and port == 4:
            datas['light'] = str(input.get('data'))


'''-----Main Activity-----'''

webbrowser.open('http://127.0.0.1:8081/')

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)


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
#Polling
@app.route('/poll', methods=['GET'])
def res():
    global datas
    responce = 'knobdata ' + datas["knob"] + '\n' + \
               'knobbuttondata ' + datas["knobbutton"] + '\n' + \
               'tempdata ' + datas["temp"] + '\n' + \
               'humiddata ' + datas["humid"] + '\n' + \
               'pascaldata ' + datas["pascal"] + '\n' + \
               'lightdata ' + datas["light"] + '\n'+ \
               'distancedata ' + datas["distance"] + '\n'

    value = str(responce)
    resp = make_response(value)
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#LEDs
@app.route('/<port>/<id>/<data>', methods=['GET'])
def led(port, id, data):
    if port == "red":
        led = 1
    elif port == "green":
        led = 2
    elif port == "blue":
        led = 3
    command = "/1001-0/" + str(led) + " " + str(data) + "\n"
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route('/leds/<id>/<red>/<green>/<blue>', methods=['GET'])
def leds(id, red, green, blue):
    command = "/1001-0/1 " + str(red) + "\n" \
              "/1001-0/2 " + str(green) + "\n" \
              "/1001-0/3 " + str(blue) + "\n"
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

#knob
@app.route('/knob/<id>', methods=['GET'])
def knob(id):
    command = "/1007-0/1\n"
    global datas
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route('/knobbutton/<id>', methods=['GET'])
def knobbutton(id):
    command = "/1007-0/2\n"
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

@app.route('/knobreset/<id>', methods=['GET'])
def knobreset(id):
    command = "/1007-0/1 0\n"
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

#temp
@app.route('/temp/<id>', methods=['GET'])
def temp(id):
    command = "/1003-0/1\n"
    global datas
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#humid
@app.route('/humid/<id>', methods=['GET'])
def humid(id):
    command = "/1003-0/2\n"
    global datas
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#pressure
@app.route('/pascal/<id>', methods=['GET'])
def pascal(id):
    command = "/1003-0/3\n"
    global datas
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

#light
@app.route('/light/<id>', methods=['GET'])
def light(id):
    command = "/1003-0/4\n"
    global datas
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

#motor
@app.route('/motor_rotate/<id>/<data>', methods=['GET'])
def motor_rotate(id, data):
    command = "/1005-0/1 " + str(data) + "\n"
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route('/motor_stop/<id>', methods=['GET'])
def motor_stop(id):
    command = "/1005-0/1 0\n"
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

# distance sensor
@app.route('/distance/<id>', methods=['GET'])
def distance(id):
    command = "/100a-0/1\n"
    global datas
    serial_conversation(command.encode())

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


'''-----Web APIs-----'''

@app.route('/api/postport', methods=['POST'])
def postport():
    port = request.form.get('port-selector')
    if 'ser' in globals():
        ser.close()
    else:
        global ser
        ser = serial.Serial(port, 115200,  timeout=0)
    return redirect("http://127.0.0.1:8081/", code=302)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)
