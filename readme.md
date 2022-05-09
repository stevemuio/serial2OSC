**Serial to OSC**

Steve Symons 2022

**Premise**
Takes a line of text from serial and turns it into OSC.

e.g.
    analog:123:234:55:789

    becomes either (composite oscmode - default)
      /analog 123 234 55 789
    or, in individual oscmode
      /analog/1 123
      /analog/2 234

**Pre-requisites**
pySerial      https://pypi.org/project/pyserial/
python-osc    https://pypi.org/project/python-osc/
python3

**Usage**
From serial2OSC folder

Loads default configuration: localhost, port 9000, composite oscmode

  $python3 serial2OSC

  or if you enable execute permissions then

  $./serial2OSC

Arguments:
--serial /dev/xxxxxxx       :the serial port you want to use, prints out available ports if not accessible.     
--port P                    :Destination port P (default is 9000)
--ip xxx.xxx.xx.xx          :Destination IP xxx.xxx.xx.xx (default localhost)       
--oscmode c or i            :Set oscmode as composite c (default) or indivdualal
--config ffff.json          :Use an external json configuration file


**Configuration file**

    $python3 serial2OSC --config IIL-yew-config.json

You can set all the above in a config file - you can then use arguments to override this.

Allows you to scale, invert and adjust your data before sending.  

e.g.
"analog":{
  "1":{"map":[1490,2630,-1,1]},
  "2":{"map":[1460,2570,1,-1]},
  "4":{"map":[0,4096,1,0]}

  The first second and fourth analog data points received will be scaled, but number three will just be send as received.

  "map":[a,b,c,d] will scale a received value V, [minInput, maxInput, minOutput, maxOutput]
    mapped value= c+(v-a)*(d-c)/(b-a)

  Different mappings such as log scale will be added.
