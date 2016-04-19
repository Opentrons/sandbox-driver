# sandbox-driver
testing new driver code for communication with smoothieboard


This code handles communication with devices (eg Smoothieboard). It is made up of the following modules:
- [driver_client.py](#driver_clientpy)
- [smoothie_driver.py](#smoothie_driverpy)


---
## driver_client.py:

This module connects to other application componenents (Frontend, Crossbar, Ser2net, etc.) using Crossbar.io 
and WAMP, and interfaces with device drivers (e.g. smoothie_driver.py) to communicate with devices.


topic = {
    'frontend' : 'com.opentrons.frontend',
    'driver' : 'com.opentrons.driver',
    'labware' : 'com.opentrons.labware',
    'bootloader' : 'com.opentrons.bootloader'
}

Incoming and Outgoing Data Format:

```
{
	'type': string,
	'to': uuid-string,
	'from': uuid-string,
	'sessionID': uuid-string,
	'data':
	{
		'name': string,
		'message': { message : param }
	},
	'time': timestamp
}
```





---
## smoothie_driver.py

This module interfaces with the Smoothieboard. It uses a TCP connection to a port that is connected 
via Ser2net to a USB serial connection from the Smoothieboard.

state_dict:
* 'name' - a device should have a name so it can be referenced
* 'simulation' - is the device is running in simulation mode?
* 'connected' - is the device connected?
* 'transport' - is the transport there? (asyncio)
* 'locked' - is the driver locked from sending data to device? (flow control)
* 'ack_received' - is there acknowledgement data received from device
* 'ack_ready' - is there acknowledgement device is ready to receive data
* 'queue_size' - size of the command queue
* 'direction':{'X':0, ... , 'C':0} - direction of given axis
* 's_pos':{'X':0, ... , 'C':0} - smoothie's record of position
* 'a_pos':{'X':0, ... , 'C':0} - adjusted (actual) position


config_dict:
* 'delimiter' - delimiter to use when parsing incoming data into individual messages (default is "\n")
* 'message_ender' - suffix to put on all data going to device (terminator string)
* 'ack_received_message' - message used to acknowledge data received from device (Smoothieboard uses "ok")
* 'ack_received_parameter' - parameter used to acknowledge data received from device (Smoothieboard does not use this)
* 'ack_received_value' - parameter or message value used to acknowledge data received from device (Smoothieboard does not use this)
* 'ack_ready_message' - message used to acknowledge device ready to receive data (Smoothieboard uses 'stat' for this)
* 'ack_ready_parameter' - parameter used to acknowledge device ready to receive data (Smoothieboard does not use this)
* 'ack_ready_value' - parameter or message value used to acknowledge device ready to receive data (Smoothieboard uses 0 for this)
* 'x_slack' - parameter used to adjust position


callbacks_dict:

The callbacks_dict is where custom callbacks are stored to listen for particular messages and then transmit 
data accordingly. This dictionary starts out empty but has the following format:

```
{
	callback name:
	{
		'callback': callback oeject,
		'messages': [ list of messags ]
	},
	...
}
```

Data subsequently transmitted to a given callback is of the form:

{ message: { param:value, ... } }

It is important to note that a large amount of useful data comes back without a "message". By default, such 
data gets attached to the message 'None', so almost all devices should have a callback for 'None' messages. 
For the Smoothieboard, that callback is called none.


meta_callbacks_dict:

The meta_callbacks_dict is important for triggering callbacks based on the driver itself, not data coming 
from the device. The meta-callback-names, previously listed as well, are:
		'on_raw_data'
		'on_connect'
		'on_empty_queue'
		'on_disconnect'

The names correspond with the event that triggers them. It is important to note that 'on_empty_queue' is 
useful for other sections of code to know that a particular set of commands has completed running, for 
instance, when running a protocol.


commands_dict:

This dictionary has all of the commands that can be sent to the device and varies by device. 
The dictionary of commands for the Smoothieboard is too long to include here, but this is the format:

```
{
	command:
	{
		'code': string code,
		'parameters': [ list of acceptable parameter strings ]
	},
	...
}
```

clear_queue clears the command_queue



* The Smoothieboard does not use checksums to verify messages, however other boards, like TinyG do. A mechanism for 
handling that could be added




[sandbox-driver](#sandbox-driver)

---
TODO: 
* Complete commands dictionary for Smoothieboard.
* Some examples of commands and their responses.
* Error reporting to Frontend, Bootstrapper
* 











