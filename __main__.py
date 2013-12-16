import sys
import signal
import re
import pysvg.parser
import usb.core
import usb.util
import threading

from gi.repository import Gtk, Gdk

preamb = 'FN0\x03FX%p,0\x03FY%t\x03FU9999,9999\x03!%s,0\x03FC18\x03FM1\x03TB50,0\x03FO9999,9999' +\
	'\x03&100,100,100\x03\30,30\x03Z9999,9999\x03L0\x03'

epilog = '&1,1,1\x03TB50,0\x03FO0\x03H'

class UsbDevice:

	def __init__(self):
		# Find device
		self.dev = usb.core.find(idVendor=0x0b4d, idProduct=0x1121)
		if self.dev is None:
			raise Exception("No matching device found")

		# Attempt to take device away from kernel
		self.reattach = False
		if self.dev.is_kernel_driver_active(0):
			self.reattach = True
	
			try:
				self.dev.detach_kernel_driver(0)
			except usb.core.USBError as e:
				raise Exception("Could not detatch kernel driver: %s" % str(e))

		self.dev.set_configuration()

		cfg = self.dev.get_active_configuration()
		interface_number = cfg[(0,0)].bInterfaceNumber
		alternate_setting = usb.control.get_interface(self.dev, interface_number)
		intf = usb.util.find_descriptor(
			cfg, bInterfaceNumber = interface_number,
			bAlternateSetting = alternate_setting
		)

		self.ep = usb.util.find_descriptor(
			intf,
			custom_match = \
			lambda e: \
			usb.util.endpoint_direction(e.bEndpointAddress) == \
			usb.util.ENDPOINT_OUT
		)

		assert self.ep is not None

	def __del__(self):
		if self.reattach:
			self.dev.attach_kernel_driver(0)
		pass

	def writeData(self, data, gui):
		for i in xrange(0, len(data), 10):
			if not gui.cuttingCallback((float(i)/len(data))*100):
				self.ep.write(data[i:i+10], -1)
			else:
				#TODO What happens if there are incomplete commands?
				#gui.pushMessage("Canceling...")
				self.ep.write(epilog)
				break
		gui.cuttingFinishedCallback()

class Gui:
	class Handler:
		def __init__(self, gui):
			self.gui = gui

		def onDeleteMainWindow(self, *args):
			self.gui.parent.quit()

		def onButtonQuit(self, *args):
			self.gui.parent.quit()

		def onButtonOpen(self, *args):
			self.gui.filechooser.run()

		def onButtonCut(self, *args):
			if self.gui.statecutting:
				self.gui.cancelflag = True
			else:
				if self.gui.parent.movements != []:
					data = "\x03".join(self.gui.parent.movements)

					params = preamb.replace("%s", str(int(self.gui.speed.get_value())))
					params = params.replace("%p", str(int(self.gui.pressure.get_value())))
					params = params.replace("%t", "1" if self.gui.trackenhance.get_active() else "0")

					data = params + data + epilog
					self.gui.setCuttingState()
					writer = threading.Thread(target=self.gui.parent.plotter.writeData, args=(data,self.gui))
					writer.start()
					self.gui.setCuttingState()
					#self.gui.parent.plotter.writeData(data,self.gui)

				else:
					print "Nothing to cut"

		def onSelectFile(self, *args):
			path = self.gui.filechooser.get_filename()
			self.gui.parent.openFile(path)

	def pushMessage(self, msg):
		self.statusbar.push(0, msg)

	def setCuttingState(self):
		self.statecutting = True
		self.cutbutton.set_label("Cancel Cut")
		self.quitbutton.set_sensitive(False)

	def cuttingCallback(self, progress):
		Gdk.threads_add_idle(200, self.pushMessage, "Cutting..."+str(int(progress))+"%")
		return self.cancelflag
		
	def cuttingFinishedCallback(self):
		self.statecutting = False
		self.cancelflag = False
		Gdk.threads_add_idle(200, self.cutbutton.set_label, "Cut")
		Gdk.threads_add_idle(200, self.quitbutton.set_sensitive, True)
		Gdk.threads_add_idle(200, self.pushMessage, "Ready")

	def __init__(self, parent):
		self.parent = parent

		self.builder = Gtk.Builder()
		self.builder.add_from_file("gtk/pyhoulette.glade")
		self.builder.connect_signals(self.Handler(self))

		self.width = self.builder.get_object("sb_width")
		self.width_adjustment = Gtk.Adjustment(300, 1, 10000, 1, 1, 0)
		self.width.set_adjustment(self.width_adjustment)
		self.heigth = self.builder.get_object("sb_heigth")
		self.heigth_adjustment = Gtk.Adjustment(300, 1, 10000, 1, 1, 0)
		self.heigth.set_adjustment(self.heigth_adjustment)

		self.speed = self.builder.get_object("s_speed")
		self.speed_adjustment = Gtk.Adjustment(8, 1, 10, 1, 1, 0)
		self.speed.set_adjustment(self.speed_adjustment)

		self.pressure = self.builder.get_object("s_pressure")
		self.pressure_adjustment = Gtk.Adjustment(6, 1, 33, 1, 1, 0)
		self.pressure.set_adjustment(self.pressure_adjustment)

		self.trackenhance = self.builder.get_object("cb_trackenhance")
		self.trackenhance.set_active(True)

		self.doublecut = self.builder.get_object("cb_doublecut")
		self.doublecut.set_active(False)

		self.statusbar = self.builder.get_object("statusbar1")
		self.pushMessage("ready!")

		self.cutbutton = self.builder.get_object("b_cut")
		self.quitbutton = self.builder.get_object("b_quit")

		self.window = self.builder.get_object("window1")

		self.filechooser = self.builder.get_object("filechooser")

		self.statecutting = False
		self.cancelflag = False

class Pyhoulette:
	def quit(self):
		print "Quitting..."
		Gtk.main_quit()

	def parseHpgl(self, data):
		self.movements = []
		hpgl = data.read().split(";", -1)
		hpgl = filter(lambda x: x.startswith(("PU","PD")), hpgl)
		movements = map(lambda x: x.replace("PU", "M"), hpgl)
		movements = map(lambda x: x.replace("PD", "D"), movements)
		for command in movements:
			values = map(int, re.findall(r'\d+', command))
			values = [int(value/2) for value in values]
			values.reverse()
			self.movements.append(command[0] + ",".join(str(d) for d in values))

		print self.movements

	def openFile(self, path):
		data = open(path, "r")
		self.parseHpgl(data)
		self.gui.pushMessage("File loaded")
		
	def run(self):
		Gdk.threads_init()
		self.gui.window.show_all()
		Gtk.main()

	def __init__(self, *cmd_args):
		self.gui = Gui(self)
		self.plotter = UsbDevice()
		self.movements = []

def main(*cmd_args):
	instance = Pyhoulette(*cmd_args)
	instance.run()

if __name__ == '__main__':
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		main(*sys.argv[1:])