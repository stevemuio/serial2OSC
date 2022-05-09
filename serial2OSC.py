#!/usr/bin/env python3

"""
pySerialOSCdaemon
Steve Symons 2022

v02
- added composote or individual OSC messaging
v03
uses a config file

todo
- check if config file there and not crash is not.
- hard code default JSON core options and change argparse setction to ref these not 'none'
- args override config file
"""
import argparse
import random
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client

import serial
import serial.tools.list_ports as serialTools

import json

global configData

def loadConfigJSON(fileName):
  global configData
  # Opening JSON file
  f = open(fileName,"r")

  # a dictionary
  configData = json.load(f)
  #print(configData)
def mapValue(value, mapAr):
    v = ( mapAr[2]+(value - mapAr[0])*(mapAr[3]-mapAr[2])/float(mapAr[1]-mapAr[0])  )
    '''
    if (abs(v)>=abs(mapAr[2])):
        return mapAr[2]
    if (abs(v)>=abs(mapAr[3])):
        return mapAr[3]
    '''
    return v

def scaleOutput(addr, id, value):
    #first do we have scale value?

    if(id in configData[addr]):
        #ok we are scaling
        if('map' in configData[addr][id]):
            return mapValue(value, configData[addr][id]['map'] )
    return value



if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="none",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=-100,
      help="The port the OSC server is listening on")
  parser.add_argument("--serial", default='none',
      help="The serial port to access - baud fixed at 115200")
  parser.add_argument("--oscmode", default='d',
      help="OSC message style c (composite, default) for /address 11 12 13 , or i (individual) for /address/1 11 ")
  parser.add_argument("--config", default="none",
        help="The over riding config file")
  args = parser.parse_args()

  #loadconfigs
  loadConfigJSON("default-config.json")


  #overide with arguments
  if (args.ip!="none"):
      configData['configure']['ip'] = args.ip
  if (args.port>0):
      configData['configure']['port'] = args.port
  if (args.oscmode!='d'):
      configData['configure']['oscmode'] = args.oscmode
  if (args.serial!='none'):
      configData['configure']['serial'] = args.serial
  if (args.config!='none'):
      loadConfigJSON(args.config)

  client = udp_client.UDPClient(configData['configure']['ip'], configData['configure']['port'])
  oscmode = configData['configure']['oscmode']
  serialName = configData['configure']['serial']

  # '/dev/tty.wchusbserial1420' configure the serial connections (the parameters differs on the device you are connecting to)
  try:
      ser = serial.Serial(
            port=serialName,
            baudrate=115200,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.SEVENBITS
      )


      ser.isOpen();

  except serial.serialutil.SerialException as err:
      print("Serial port error.. try one of these");
      print(*list(serialTools.comports()))
      quit();
 # board = ArduinoMega('/dev/cu.usbmodem1411')
  #print(board)

  out=""
  c = ''
  print(configData['configure']['ip'])
  while (1):
    cmd = str(ser.readline())
    #print(cmd)
    cmdAr = cmd[2:(len(cmd)-5)].split(':')
    #print(cmdAr)
    if len(cmdAr)>1:
        if (oscmode == 'c'):
              msg = osc_message_builder.OscMessageBuilder(address = "/"+cmdAr[0])
              for i in range(1,len(cmdAr)):
                 msg.add_arg(scaleOutput(cmdAr[0], str(i), float(cmdAr[i])))
              msg = msg.build()
              client.send(msg)
        else:
              for i in range(1,len(cmdAr)):
                 msg = osc_message_builder.OscMessageBuilder(address = "/"+cmdAr[0]+"/"+str(i))
                 msg.add_arg(scaleOutput(cmdAr[0], str(i), float(cmdAr[i])))
                 msg = msg.build()
                 client.send(msg)

    time.sleep(0.001)
