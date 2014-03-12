QuickCoords
===========

*QuickCoords* aims to be a simple tool for quickly and easily capturing a series of pixel coordinates from an image.

The focus is on speed and optimised work flow.

It is being written in Python 3 using PyQt4.


Usage
-----

At the moment, the tool can only be run directly from the source using the command:
	
	python QuickCoords.py
	
The path environment variable needs to be set to point to your python installation directory, if it doesn't already.


Keys
----

* Arrow keys will scroll the image if it has focus.
* D K + . ] and > move to the next image.
* A J - , [ and < move to the previous image.
* Clicking on the image will add the coordinates of that pixel to the list on the right.
* Right clicking or Backspace will delete the last point on the list.
* Delete will delete the selected points from the list.


License
-------

*QuickCoords* is copyright (c) 2014, Brendan Gray and Sylvermyst Technologies under an MIT license.

A copy of the license should have been included with the software. If not, it is available from [http://opensource.org/licenses/MIT].
