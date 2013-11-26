import sys
import signal
import pysvg.parser

from gi.repository import Gtk

class Gui:
	class Handler:
		def __init__(self, gui):
			self.gui = gui

		def onDeleteMainWindow(self, *args):
			quit()

		def onButtonQuit(self, *args):
			quit()

		def onButtonOpen(self, *args):
			self.gui.filechooser.run()

		def onSelectFile(self, *args):
			path = self.gui.filechooser.get_filename()
			self.gui.parent.openFile(path)

	def pushMessage(self, msg):
		self.statusbar.push(0, msg)

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

		self.statusbar = self.builder.get_object("statusbar1")
		self.pushMessage("ready!")

		self.window = self.builder.get_object("window1")

		self.filechooser = self.builder.get_object("filechooser")

class Pyhoulette:
	def quit(self):
		print "Quitting..."
		Gtk.main_quit()

	def parseHpgl(self, data):
		hpgl = data.read().split(";", -1)
		hpgl = filter(lambda x: x.startswith(("PU","PD")), hpgl)
		movements = map(lambda x: x.replace("PU", "M"), hpgl)
		self.movements = map(lambda x: x.replace("PD", "D"), movements)
		print self.movements

	def openFile(self, path):
		data = open(path, "r")
		self.parseHpgl(data)
		self.gui.pushMessage("File loaded")

		
	def run(self):
		self.gui.window.show_all()
		Gtk.main()

	def __init__(self, *cmd_args):
		self.gui = Gui(self)
		self.movements = []

def main(*cmd_args):
	instance = Pyhoulette(*cmd_args)
	instance.run()

if __name__ == '__main__':
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		main(*sys.argv[1:])