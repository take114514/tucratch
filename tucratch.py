#!/usr/bin/env python
# -*- coding: utf8 -*-

import webbrowser
import serial
import serial.tools.list_ports
import json
from flask import Flask, render_template, request, redirect


'''------Functions------'''


def serial_ports():
    ports = serial.tools.list_ports.comports()
    port_list = []
    for port in ports:
        port_list.append(port.device)
    return port_list


'''-----Main Activity-----'''

webbrowser.open('http://127.0.0.1:5000/')

app = Flask(__name__)
datas = {
    "knob": "0",
    "temp": "0",
    "humid": "0",
    "pascal": "0",
    "ph": "0",
    "co2": "0",
    "co2temp": "0"
}

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
               'phdata ' + datas["ph"] + '\n' + \
               'co2data ' + datas["co2"] + '\n' + \
               'co2tempdata ' + datas["co2temp"] + '\n'
    return responce


#LEDs
@app.route('/<port>/<id>/<data>', methods=['GET'])
def led(port, id, data):
    if port == "red":
        led = 1
    elif port == "green":
        led = 2
    elif port == "blue":
        led = 3
    command = "/1001-0/" + str(led) + "/" + str(data) + "\n"
    ser.write(command.encode())
    ser.readline()
    return 'OK'


@app.route('/leds/<id>/<red>/<green>/<blue>', methods=['GET'])
def leds(id, red, green, blue):
    command1 = "/1001-0/1/ " + str(red) + "\n"
    ser.write(command1.encode())
    ser.readline()
    command2 = "/1001-0/2/ " + str(green) + "\n"
    ser.write(command2.encode())
    ser.readline()
    command3 = "/1001-0/3/" + str(blue) + "\n"
    ser.write(command3.encode())
    ser.readline()
    return 'OK'


#knob
@app.route('/knob/<id>', methods=['GET'])
def knob(id):
    command = "/1007-0/1\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['knob'] = str(data.get('data'))
    return 'OK'


@app.route('/knobbutton/<id>', methods=['GET'])
def knobbutton(id):
    command = "/1007-0/2/\n"
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['knobbutton'] = str(data.get('data'))
    return 'OK'


#temp
@app.route('/temp/<id>', methods=['GET'])
def temp(id):
    command = "/1003-0/1\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['temp'] = str(data.get('data'))
    return 'OK'


#humid
@app.route('/humid/<id>', methods=['GET'])
def humid(id):
    command = "/1003-0/2\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['humid'] = str(data.get('data'))
    return 'OK'


#pressure
@app.route('/pascal/<id>', methods=['GET'])
def pascal(id):
    command = "/1003-0/3\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['pascal'] = str(data.get('data'))
    return 'OK'


#ph
@app.route('/ph/<id>', methods=['GET'])
def ph(id):
    command = "/1008-0/1\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['ph'] = str(data.get('data'))
    return 'OK'


#co2
@app.route('/co2/<id>', methods=['GET'])
def co2(id):
    command = "/1009-0/1\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['co2'] = str(data.get('data'))
    return 'OK'


#co2-temp
@app.route('/co2temp/<id>', methods=['GET'])
def co2temp(id):
    command = "/1009-0/2\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['co2temp'] = str(data.get('data'))
    return 'OK'


#motor1
@app.route('/motor_rotate1/<id>/<data>', methods=['GET'])
def motor_rotate1(id, data):
    command = "/1005-0/1/" + str(data) + "\n"
    ser.write(command.encode())
    ser.readline()
    return 'OK'


@app.route('/motor_stop1/<id>', methods=['GET'])
def motor_stop1(id):
    command = "/1005-0/1/0\n"
    ser.write(command.encode())
    ser.readline()
    return 'OK'


#motor2
@app.route('/motor_rotate2/<id>/<data>', methods=['GET'])
def motor_rotate2(id, data):
    command = "/1005-0/2/" + str(data) + "\n"
    ser.write(command.encode())
    ser.readline()
    return 'OK'


@app.route('/motor_stop2/<id>', methods=['GET'])
def motor_stop2(id):
    command = "/1005-0/2/0\n"
    ser.write(command.encode())
    ser.readline()
    return 'OK'


'''-----Web APIs-----'''

@app.route('/api/postport', methods=['POST'])
def postport():
    port = request.form.get('port-selector')
    print port
    if 'ser' in globals():
        ser.close()
    else:
        global ser
        ser = serial.Serial(port, 9600)
    return redirect("http://127.0.0.1:5000/", code=302)

app.run(threaded=True)
