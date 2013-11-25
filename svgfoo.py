import pysvg.parser
import sys

svg = pysvg.parser.parse(sys.argv[1])
print svg.get_width(), svg.get_height()
elements = svg.getAllElementsOfHirarchy()

for e in elements:
	if isinstance(e, pysvg.shape.Rect) or isinstance(e, pysvg.shape.Path):
			print e.getAttributes()
			print '\n'