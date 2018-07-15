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
    "temp": "0",
    "humid": "0",
    "pascal": "0",
    "ph": "0",
    "co2": "0",
    "co2temp": "0"
}

#Polling
@app.route('/poll', methods=['GET'])
def res():
    global datas
    responce = 'knobdata ' + datas["knob"] + '\n' + 'tempdata ' + datas["temp"] + '\n' + 'humiddata ' + datas["humid"] + '\n' + 'pascaldata ' + datas["pascal"] + '\n' + 'phdata ' + datas["ph"] + '\n' + 'co2data ' + datas["co2"] + '\n' + 'co2tempdata ' + datas["co2temp"] + '\n'
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
    command = "post -b 1001-0 -p " + str(led) + " -t int16 " + str(data) + "\n"
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


@app.route('/knobreset/<id>', methods=['GET'])
def knobreset(id):
    command = "/1007-0/1/0\n"
    ser.write(command.encode())
    ser.readline()
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
