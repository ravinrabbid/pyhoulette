import sys
from gi.repository import Gtk

def quit():
	print "Quitting..."
	Gtk.main_quit()

class Gui:

	class Handler:
		def onDeleteMainWindow(self, *args):
			quit()

		def onButtonQuit(self, *args):
			quit()

	def __init__(self):
		self.builder = Gtk.Builder()
		self.builder.add_from_file("gtk/pyhoulette.glade")
		self.builder.connect_signals(self.Handler())

		self.width = self.builder.get_object("sb_width")
		self.width_adjustment = Gtk.Adjustment(300, 1, 350, 1, 1, 0)
		self.width.set_adjustment(self.width_adjustment)
		self.heigth = self.builder.get_object("sb_heigth")
		self.heigth_adjustment = Gtk.Adjustment(300, 1, 350, 1, 1, 0)
		self.heigth.set_adjustment(self.heigth_adjustment)

		self.speed = self.builder.get_object("s_speed")
		self.speed_adjustment = Gtk.Adjustment(8, 1, 10, 1, 1, 0)
		self.speed.set_adjustment(self.speed_adjustment)

		self.pressure = self.builder.get_object("s_pressure")
		self.pressure_adjustment = Gtk.Adjustment(6, 1, 33, 1, 1, 0)
		self.pressure.set_adjustment(self.pressure_adjustment)

		self.statusbar = self.builder.get_object("statusbar1")
		self.statusbar.push(0, "ready!")

		self.window = self.builder.get_object("window1")

def main(*cmd_args):
	gui = Gui()
	gui.window.show_all()
	Gtk.main()

if __name__ == '__main__':
        main(*sys.argv[1:])