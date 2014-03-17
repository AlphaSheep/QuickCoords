'''
QuickCoords/image.py

QuickCoords is a simple tool for quickly and easily capturing a series of pixel 
coordinates from a large number of images.

    Copyright (c) 2014, Brendan Gray and Sylvermyst Technologies
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

This module provides the ClickableImageBox class.

'''

from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from QuickCoords.points import Point
from QuickCoords.constants import imageScaleFactor


class ClickableImageBox(QtGui.QGraphicsScene):
    '''
    Extends the QGraphicsScene to provide additional functionality.
    Provides the following function:
        ClickableImageBox.mouseReleaseEvent(event, *args, **kwargs) handles clicking to add and select points on the image.
    '''
    
    def mouseReleaseEvent(self, *args, **kwargs):
        '''
        Handles left clicking to add and select points on the image and right clicking to remove the last point,
        then calls the mouseReleaseEvent() method of the QGraphicsScene.
        '''        
        
        event = args[0]
        if event.button() == Qt.LeftButton:
            point = Point(event.scenePos().x()/imageScaleFactor, event.scenePos().y()/imageScaleFactor)
            nearPoint = self.parent().coordList.getPointIndex(point)
            if nearPoint >= 0:
                # The point is an existing point
                selectedPoints = self.parent().table.getSelectedPoints()
                if not nearPoint in selectedPoints:
                    # The point exists, but is not yet selected.
                    if event.modifiers() & (Qt.ShiftModifier | Qt.ControlModifier):
                        # If Shift or Ctrl are being pressed, add the point to the current selection.
                        selectedPoints.append(nearPoint)
                    else:
                        # Otherwise, the point becomes the current selection.
                        selectedPoints = [nearPoint]
                else:
                    # The point already exists, and is already selected.
                    if event.modifiers() & Qt.ControlModifier:
                        # If Ctrl is being pressed, remove the point from the selection.
                        selectedPoints.remove(nearPoint)
                    elif not (event.modifiers() & Qt.ShiftModifier):
                        # Otherwise, deselect all other points. 
                        selectedPoints = [nearPoint]
                self.parent().table.setSelectedRows(selectedPoints)
                
            else:
                self.parent().coordList.addPoint(point)
                
        if event.button() == Qt.RightButton:
            self.parent().coordList.removeLastPoint()
            
        self.parent().tableViewChanged = True

        return QtGui.QGraphicsScene.mouseReleaseEvent(self, *args, **kwargs)
