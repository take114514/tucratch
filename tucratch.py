#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import glob
import serial
import threading
from flask import Flask
import wx
import json
global ser
global name

'''------Functions------'''

def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def combobox_event(event):
    global name
    obj = event.GetEventObject()
    name = obj.GetStringSelection()
    server.start()

def run_server():
    global ser
    global name
    ser = serial.Serial(name, 9600)
    app.run()

'''-----Define Frask Activity-----'''

app = Flask(__name__)
datas = {
    "knob": "0",
    "button": "0",
    "light": "0",
    "temp": "0",
    "pascal": "0",
    "person": "0"
}

#Polling
@app.route('/poll', methods=['GET'])
def res():
    global datas
    responce = 'knobdata ' + datas["knob"] + '\n' + \
               'buttondata ' + datas["button"] + '\n' + \
               'lightdata ' + datas["light"] + '\n' + \
               'tempdata ' + datas["temp"] + '\n' + \
               'pascaldata ' + datas["pascal"] + '\n' + \
               'persondata ' + datas["person"] + '\n'
    return responce


#Bridge

@app.route('/bridge/<id>', methods=['GET'])
def bridge(id):
    command = "bridge"
    ser.write(command.encode())
    ser.readline()
    return 'OK'


#motor
@app.route('/motor/<data>', methods=['GET'])
def motor(data):
    command = "post -b 1005-0 -p 1 -t int16 " + str(data) + "\n"
    ser.write(command.encode())
    ser.readline()
    return 'OK'

@app.route('/motorstop', methods=['GET'])
def motorstop():
    command = "post -b 1005-0 -p 1 -t int16 0\n"
    ser.write(command.encode())
    ser.readline()
    return 'OK'

#LEDs
@app.route('/<port>/<data>', methods=['GET'])
def led(port, data):
    if port == "red":
        led = 1
    elif port == "green":
        led = 2
    elif port == "blue":
        led = 3
    command = "post -b 1001-0 -p " + str(led) + " -t int16 " + str(data) + "\n"
    ser.write(command.encode())
    ser.readline()
    return 'OK'

@app.route('/leds/<red>/<green>/<blue>', methods=['GET'])
def leds(red, green, blue):
    command1 = "post -b 1001-0 -p 1 -t int16 " + str(red) + "\n"
    ser.write(command1.encode())
    ser.readline()
    command2 = "post -b 1001-0 -p 2 -t int16 " + str(green) + "\n"
    ser.write(command2.encode())
    ser.readline()
    command3 = "post -b 1001-0 -p 3 -t int16 " + str(blue) + "\n"
    ser.write(command3.encode())
    ser.readline()
    return 'OK'


#knob
@app.route('/knob/<id>', methods=['GET'])
def knob(id):
    command = "get -b 1007-0 -p 1 -t int16 \n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['knob'] = str(data.get('data'))
    return 'OK'


@app.route('/knobreset/<id>', methods=['GET'])
def knobreset(id):
    command = "post -b 1007-0 -p 1 -t int16 0 \n"
    ser.write(command.encode())
    ser.readline()
    return 'OK'

#light
@app.route('/light/<id>', methods=['GET'])
def light(id):
    command = "get -b 1003-0 -p 4 -t float \n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['light'] = str(data.get('data'))
    return 'OK'

#temp
@app.route('/temp/<id>', methods=['GET'])
def temp(id):
    command = "get -b 1003-0 -p 1 -t float \n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['temp'] = str(data.get('data'))
    return 'OK'

#pressure
@app.route('/pascal/<id>', methods=['GET'])
def pascal(id):
    command = "get -b 1003-0 -p 3 -t float \n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['pascal'] = str(data.get('data'))
    return 'OK'

#person
@app.route('/person/<id>', methods=['GET'])
def person(id):
    command = "get -b 1004-0 -p 1 -t bool \n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['person'] = str(data.get('data'))
    return 'OK'

#button
@app.route('/button/<id>', methods=['GET'])
def button(id):
    command = "get -b 1007-0 -p 2 -t bool \n"
    global datas
    ser.write(command.encode())
    line = ser.readline()
    data = json.loads(line)
    datas['button'] = str(data.get('data'))
    return 'OK'

'''-----Define wxPython Activity-----'''

server = threading.Thread(target=run_server, name="server")
server.daemon = True

app2 = wx.App()

frame = wx.Frame(None, -1, u'Tucratch', size=(250,50))
panel  = wx.Panel(frame, -1)

combo = wx.ComboBox(panel, -1, u'choices', choices=serial_ports(), style=wx.CB_READONLY)

combo.Bind(wx.EVT_COMBOBOX, combobox_event)

frame.Show()
app2.MainLoop()
