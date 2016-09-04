# pyhoulette
Plot Inkscape generated hpgl files on your Silhoutte Cameo

<a href="url"><img src="https://raw.githubusercontent.com/ravinrabbid/pyhoulette/master/screen.jpg" width="300" ></a>
## Requirements
- pyusb
- pygtk
- python-gobject

## Installation
pyhoulette needs access to your plotter, either use the udev rule below or
set the appropriate permissions yourself:

```
ATTRS{idVendor}=="0b4d", ATTRS{idProduct}=="1121", MODE="666", ENV{silhouette_cameo}="yes", OPTIONS="last_rule"
```

## Usage
Select the desired HPGL file and adjust the parameters, then click "Cut".

## Notes
- Currently the Size options are ignored, make sure the inserted medium is large enough yourself.
- "Cancel" does not stop cutting instantly, the plotter buffers commands which will be cut.
Use the hardware buttons on the plotter to instantly cancel cutting.
- The software expects HPGL files generated with Inkscape <=0.48.5 default settings (flatness 0.2, resolution 1016).
Newer versions of Inkscape produce HPGL files with unsatisfying cut results, consider installing the old export plug-in as described below.
- For a more sophisticated approach on cutting from Inkscape, have a look at [inkscape-silhouette](https://github.com/fablabnbg/inkscape-silhouette)

### Getting the old export
- Download Inkscape 0.48.5 [sources](https://inkscape.org/en/download/)
- Extract /share/extensions/hpgl_output.* to ~/.config/inkscape/extensions/hpgl_output_old.*
- Change the following tags in the .inx:
```
<_name>HPGL Output Old</_name>
<id>org.ekips.output.hpglold</id>
...
<dependency type="executable" location="extensions">hpgl_output_old.py</dependency>
...
    <_filetypename>HP Graphics Language file - old (*.hpgl)</_filetypename>
...
    <command reldir="extensions" interpreter="python">hpgl_output_old.py</command>
```
- Remember to select the correct export plugin (HP Graphics Language file - old (*.hpgl)) in the "Save as..." dialogue
