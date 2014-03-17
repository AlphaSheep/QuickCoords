'''
QuickCoords/table.py

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

This module provides the TableBox class

'''

from PyQt4 import QtGui
from QuickCoords.points import CoordinateList

class TableBox(QtGui.QTableWidget):
    '''
    Extends QTableWidget to provide the following functions:
        TableBox.keyPressEvent(event, *args, **kwargs) Unnecessary function. To be removed.
        TableBox.deleteSelectedRows() deletes all points that are currently selected.
        TableBox.selectionChanged(*args, **kwargs) changes the colours of points depending on whether or not they are selected.
        TableBox.getSelectedPoints() returns a list of the currently selected points.
        TableBox.setSelectedRows(rows) Selects all points in the list of indices.
        
    '''
    
    def keyPressEvent(self, *args, **kwargs):
        '''
        Unnecessary function. To be removed.
        '''
        
        event = args[0]
        self.toolScreen.ignoreDeletes = True
        self.toolScreen.keyPressEvent(event)
        return QtGui.QTableWidget.keyPressEvent(self, *args, **kwargs)
    
    
    def deleteSelectedRows(self):
        '''
        Deletes all rows that are currently selected and updates the parent's coordinate list.
        '''
        
        newCoordList = CoordinateList([])
        oldCoordList = self.toolScreen.coordList

        selectedPoints = self.getSelectedPoints()
        
        for i in range(self.rowCount()):
            if not i in selectedPoints:
                newCoordList.addPoint(oldCoordList.points[i])
        self.toolScreen.coordList = newCoordList
        self.setSelectedRows([])
        
    
    def selectionChanged(self, *args, **kwargs):
        '''
        Updates the point colours if they are selected.
        '''
        
        selectedPoints = self.getSelectedPoints()
        
        for i in range(self.toolScreen.coordList.length()):
            if i in selectedPoints:
                self.toolScreen.coordList.points[i].colour = 1
            else:
                self.toolScreen.coordList.points[i].colour = 0            
        self.toolScreen.tableViewChanged = True
                
        return QtGui.QTableWidget.selectionChanged(self, *args, **kwargs)
    
    
    def getSelectedPoints(self):
        '''
        Returns a list of the currently selected points.  
        '''
        
        selectedPoints = []
        for index in self.selectionModel().selectedRows():
            selectedPoints.append(index.row())
        return selectedPoints
            
        
    def setSelectedRows(self, rows):
        '''
        Selects all points specified in rows, which is a list of indices to be selected.
        '''
        
        self.clearSelection()
        selectedItems = self.selectionModel().selection()
        for i in rows:      
            self.selectRow(i)      
            selectedItems.merge(self.selectionModel().selection(), QtGui.QItemSelectionModel.Select)
        self.selectionModel().select(selectedItems, QtGui.QItemSelectionModel.Select)

