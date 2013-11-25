import usb.core
import usb.util

# find our device
dev = usb.core.find(idVendor=0x0b4d, idProduct=0x1121)

# was it found?
if dev is None:
    raise ValueError('Device not found')

# set the active configuration. With no arguments, the first
# configuration will be the active one
dev.set_configuration()

# get an endpoint instance
cfg = dev.get_active_configuration()
interface_number = cfg[(0,0)].bInterfaceNumber
alternate_setting = usb.control.get_interface(dev, interface_number)
intf = usb.util.find_descriptor(
    cfg, bInterfaceNumber = interface_number,
    bAlternateSetting = alternate_setting
)

ep = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT
)

assert ep is not None

# write the data

#ep.write('FN0\x03FX15,0\x03FY1\x03FU5256,5896\x03!10,0\x03FC18\x03FM1\x03TB50,0\x03FO6066,6066' +
#	'\x03&100,100,100\x03\30,30\x03Z6066,6066\x03L0\x03M875,795\x03' +
#	'D875,775,1178,775,1178,1153,875,1153,875,775,895,775\x03&1,1,1\x03TB50,0\x03FO0\x03H')
ep.write('TB50,0\x03FO2000,23\x03')

# H     		- Home Position
# !n,0  		- Speed
# FXn,0 		- Pressure
# &n,n,n		- Scale Factor (default 100,100,100)
# FNb   		- Landscape
# FYb   		- Track Enhancing
# FCn   		- Blade Offset (default 18)
# Ln    		- Line Type (default 0)
# Zn,n  		- Media Size
# TB50,0		- ????
# FM1   		- ????
# FUn,n 		- Usable area
# \n,n  		- Lower left - relative to media size
# Zn,n  		- Upper right - relative to media size
# 0FY1          - Trackenhancing?

# Transport margins are y:200 and x:840




# FN0FX15,0FY1FU5256,5896!10,0FC18FM1TB50,0FO5596,5900&100,100,100
#	\30,0Z5596,5900L0M525,511D525,491,733,491,733,1370,525,1370,525,491,545,491&1,1,1TB50,0FO0H

# FN0FX15,0FY1FU5256,5896!10,0FC18FM1TB50,0FO6066,6066&100,100,100
#	\30,30Z6066,6066L0M525,611D525,591,733,591,733,1470,525,1470,525,591,545,591&1,1,1TB50,0FO0H

# FN0FX15,0FY1FU1160,1800!10,0FC18FM1TB50,0FO1970,1970&100,100,100
#	\30,30Z1970,1970L0M0,20D0,0,200,0,200,200,0,200,0,0,20,0&1,1,1TB50,0FO0H

# FN0FX15,0FY1FU1160,1800!10,0FC18FM1TB50,0FO1970,1970&100,100,100
#	\30,30Z1970,1970L0M0,0D2000,2000M2000,0D0,2000&1,1,1TB50,0FO0H

#