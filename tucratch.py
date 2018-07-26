#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import webbrowser
import serial
import serial.tools.list_ports
import json
from flask import Flask, render_template, request, redirect, make_response

'''------Functions------'''


def serial_ports():
    ports = serial.tools.list_ports.comports()
    port_list = []
    for port in ports:
        port_list.append(port.device)
    return port_list


'''-----Main Activity-----'''

webbrowser.open('http://127.0.0.1:8081/')

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

datas = {
    "knob": "0",
    "knobbutton": "0",
    "temp1": "0",
    "humid1": "0",
    "pascal1": "0",
    "temp2": "0",
    "humid2": "0",
    "pascal2": "0",
    "ph": "0",
    "co2": "0",
    "co2temp": "0",
    "light1": "0",
    "light2": "0",
    "distance": "0"
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
               'tempdata1 ' + datas["temp1"] + '\n' + \
               'humiddata1 ' + datas["humid1"] + '\n' + \
               'pascaldata1 ' + datas["pascal1"] + '\n' + \
               'tempdata2 ' + datas["temp2"] + '\n' + \
               'humiddata2 ' + datas["humid2"] + '\n' + \
               'pascaldata2 ' + datas["pascal2"] + '\n' + \
               'phdata ' + datas["ph"] + '\n' + \
               'co2data ' + datas["co2"] + '\n' + \
               'co2tempdata ' + datas["co2temp"] + '\n' + \
               'lightdata1 ' + datas["light1"] + '\n'+ \
               'lightdata2 ' + datas["light2"] + '\n' + \
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
    ser.write(command.encode())
    ser.readline()

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route('/leds/<id>/<red>/<green>/<blue>', methods=['GET'])
def leds(id, red, green, blue):
    command1 = "/1001-0/1 " + str(red) + "\n"
    ser.write(command1.encode())
    ser.readline()
    command2 = "/1001-0/2 " + str(green) + "\n"
    ser.write(command2.encode())
    ser.readline()
    command3 = "/1001-0/3 " + str(blue) + "\n"
    ser.write(command3.encode())
    ser.readline()

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

#light1
@app.route('/light1/<id>', methods=['GET'])
def light1(id):
    command = "/1003-0/4\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['light1'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

#light2
@app.route('/light2/<id>', methods=['GET'])
def light2(id):
    command = "/1003-1/4\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['light2'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

#knob
@app.route('/knob/<id>', methods=['GET'])
def knob(id):
    command = "/1007-0/1\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['knob'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route('/knobbutton/<id>', methods=['GET'])
def knobbutton(id):
    command = "/1007-0/2\n"
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['knobbutton'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

@app.route('/knobreset/<id>', methods=['GET'])
def knobreset(id):
    command = "/1007-0/1 0\n"
    ser.write(command.encode())
    line = ser.readline()
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp



#temp1
@app.route('/temp1/<id>', methods=['GET'])
def temp1(id):
    command = "/1003-0/1\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['temp1'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#humid1
@app.route('/humid1/<id>', methods=['GET'])
def humid1(id):
    command = "/1003-0/2\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['humid1'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#pressure1
@app.route('/pascal1/<id>', methods=['GET'])
def pascal1(id):
    command = "/1003-0/3\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['pascal1'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#temp2
@app.route('/temp2/<id>', methods=['GET'])
def temp2(id):
    command = "/1003-1/1\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['temp2'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#humid2
@app.route('/humid2/<id>', methods=['GET'])
def humid2(id):
    command = "/1003-1/2\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['humid2'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#pressure2
@app.route('/pascal2/<id>', methods=['GET'])
def pascal2(id):
    command = "/1003-1/3\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['pascal2'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp



#ph
@app.route('/ph/<id>', methods=['GET'])
def ph(id):
    command = "/1008-0/1\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['ph'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#co2
@app.route('/co2/<id>', methods=['GET'])
def co2(id):
    command = "/1009-0/1\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['co2'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#co2-temp
@app.route('/co2temp/<id>', methods=['GET'])
def co2temp(id):
    command = "/1009-0/2\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['co2temp'] = str(data.get('data'))
    print line

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#motor1
@app.route('/motor_rotate1/<id>/<data>', methods=['GET'])
def motor_rotate1(id, data):
    command = "/1005-0/1 " + str(data) + "\n"
    ser.write(command.encode())
    ser.readline()

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route('/motor_stop1/<id>', methods=['GET'])
def motor_stop1(id):
    command = "/1005-0/1 0\n"
    ser.write(command.encode())
    ser.readline()

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


#motor2
@app.route('/motor_rotate2/<id>/<data>', methods=['GET'])
def motor_rotate2(id, data):
    command = "/1005-0/2 " + str(data) + "\n"
    ser.write(command.encode())
    ser.readline()

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route('/motor_stop2/<id>', methods=['GET'])
def motor_stop2(id):
    command = "/1005-0/2 0\n"
    ser.write(command.encode())
    ser.readline()

    resp = make_response('OK')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

# distance sensor
@app.route('/distance/<id>', methods=['GET'])
def distance(id):
    command = "/100a-0/1\n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['distance'] = str(data.get('data'))
    print line

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
        ser = serial.Serial(port, 9600)
    return redirect("http://127.0.0.1:8081/", code=302)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)
