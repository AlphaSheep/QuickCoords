#!/usr/bin/env python3
# coding: utf-8
'''
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

Running or building this software from source requires a working installation of Python 3 and PyQt.

'''

import sys
import os

from PyQt4.QtCore import Qt, QTimer
from PyQt4 import QtGui


#==================#
# Global constants #
#==================#

supportedExtensions = ['png', 'jpg', 'jpeg', 'bmp', 'gif']

forwardKeys = [Qt.Key_Greater, Qt.Key_Period, Qt.Key_X, Qt.Key_K, Qt.Key_Plus, Qt.Key_Equal, Qt.Key_ParenRight, Qt.Key_BraceRight, Qt.Key_BracketRight]
backwardKeys = [Qt.Key_Less, Qt.Key_Comma, Qt.Key_Z, Qt.Key_J, Qt.Key_Minus, Qt.Key_ParenLeft, Qt.Key_BraceLeft, Qt.Key_BracketLeft]

imageScaleFactor = 6
selectionRadius = 1

outputColumnMinWidth = 160
outputColumnMaxWidth = 6400
outputColumnMinHeight = 160
imageColumnMinWidth = 180

folderSaveFileName = 'lastfolder.txt'

targetFPS = 30


#===================#
# Class definitions # 
#===================#

class Point():
    '''
    Provides a basic point functionality with x, y coordinates.
        Point.shift(direction, amount) method shifts a point by a certain amount in a specified direction.
    '''
    
    def __init__(self, x, y):
        
        self.x = x
        self.y = y
        self.colour = 0
        
    
    def shift(self, direction, amount):
        '''
        Shifts the point by amount in the specified direction.
        Direction can be 'up', 'down', 'left' or 'right'.
        '''
        
        if direction == 'up':
            self.y -= amount
        elif direction == 'down':
            self.y += amount
        elif direction == 'left':
            self.x -= amount
        elif direction == 'right':
            self.x += amount
        if abs(self.x-round(self.x))<1e-8:
            self.x = round(self.x)
        if abs(self.y-round(self.y))<1e-8:
            self.y = round(self.y)
            
        
    def __str__(self):
        
        return '('+str(self.x)+', '+str(self.y)+')'


class CoordinateList():
    '''
    Provides functionality for dealing with a list of points.
    Provides the following methods:
        CoordinateList.addPoint(point) adds a point to the list.
        CoordinateList.addPoints(points) adds a list of points to the list.
        CoordinateList.removeLastPoint() removes the last point from the list.
        CoordinateList.clear() removes all points.
        CoordinateList.length() returns the length of the coordinate list.
        CoordinateList.removePoint(n) removes the point with index n.
        CoordinateList.getPointIndex(point) returns the index of a point close to the specified point.
        CoordinateList.copyAsText() returns a tab separated string of points.
        CoordinateList.copyAsCSV() returns a comma separated string of points.
    '''
    
    def __init__(self, initPoints):
        
        self.points = initPoints


    def addPoint(self, point):
        '''
        Adds a point to the coordinate list.
        '''
        
        self.points.append(point)
        
    
    def addPoints(self, points):
        '''
        Adds all points in the list of points to the coordinate list. 
        '''
        
        for p in points:
            self.points.append(p)
            
            
    def removeLastPoint(self):
        '''
        Removes the last point from the list.
        '''
        
        self.points = self.points[:-1]
    
    
    def clear(self):
        '''
        Removes all points from the list.
        '''
        
        self.points = []
        
         
    def length(self):
        '''
        Returns the number of points in the list
        '''
        
        return len(self.points)
    
    
    def removePoint(self, n):
        '''
        Removes the nth point from the list.
        '''
        
        if n >= len(self.points):
            self.points[n] # Lazily force list index out of range, otherwise it would have passed silently.
        else:
            self.points = self.points[:n] + self.points[n+1:]
        
    
    def getPointIndex(self, point):
        '''
        Finds a point in the list within selectionRadius of the specified point.
        Requires the constant selectionRadius to be defined within the current namespace.
        '''
        
        for i in range(self.length()):
            p = self.points[i]
            if abs(p.x - point.x) <= selectionRadius and abs(p.y - point.y) <= selectionRadius:
                return i
        return -1
        
    
    def copyAsText(self):
        '''
        Returns a tab separated string of points suitable for copying into spreadsheet programs such as 
        Microsoft Excel or LibreOffice Calc.  
        '''
        
        res = ''
        for p in self.points:
            res += str(p.x)+'\t'+str(p.y)+'\n'
        return res.strip()


    def copyAsCSV(self):
        '''
        Returns a comma separated string of points suitable for writing into a CSV file. 
        '''
        
        res = ''
        for p in self.points:
            res += str(p.x)+', '+str(p.y)+'\n'
        return res.strip()
        
    
    def __str__(self):
         
        res = ''
        for p in self.points:
            res += str(p)+' '
        return res.strip()


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



class ToolScreen(QtGui.QWidget):
    '''
    Extends QWidget to provide the required functionality for the program.
    Provides the following functions:
        ToolScreen.prepare() initialises some variables.
        ToolScreen.updateDisplay() fills the table and redraws the points.
        ToolScreen.keyPressEvent(event) handles keyboard shortcuts.
        ToolScreen.initUI() initialises the user interface.
        ToolScreen.selectFolder() brings up a folder selection dialogue.
        ToolScreen.setFoldertoPath(newPath) changes the current folder.
        ToolScreen.copyTable() copies the list of points to the clipboard.
        ToolScreen.exportTable() exports the list of points to a CSV or plain text file.
        ToolScreen.clearTable() deletes all points.
        ToolScreen.fillListBox() fills the list box with the images from the current folder.
        ToolScreen.changeImageFromList() changes the image to the currently selected image in the list box.
        ToolScreen.shiftSelected(direction) shifts the selected points in the specified direction.
        ToolScreen.setImage() loads the current image from disk and sets it for display.
        ToolScreen.updatePoints() updates the table to reflect the current state of the coordinate list.
        ToolScreen.drawImagePoints() redraws the points on the display.
        ToolScreen.nextImage() switches to the next image.
        ToolScreen.prevImage() switches to the previous image.
        ToolScreen.saveCurrentFolder() writes the current path to a file.
        ToolScreen.loadLastFolder() loads the folder last used.
    '''
    
    
    def __init__(self):

        super(ToolScreen, self).__init__() # Call the constructor of this class's parent        
        self.prepare()
        self.initUI()
        self.setFoldertoPath(self.imagePath)

        self.fpsTimer = QTimer()
        self.fpsTimer.timeout.connect(self.updateDisplay)
        self.fpsTimer.start(1000/targetFPS)


    def prepare(self):
        '''
        Initialises variables that need to be set before the GUI is initialised.
        '''

        self.loadLastFolder()
        self.currentImageNum = 0
        self.imageList = []
        self.coordList = CoordinateList([])
        self.scaleFactor = imageScaleFactor
        self.tableViewChanged = False
        self.ignoreDeletes = False
               
                     
    def updateDisplay(self):
        '''
        Fills the table and redraws the points, if things have changed since the last update.
        '''
        
        if self.tableViewChanged:
            self.updatePoints()
            self.drawImagePoints()
            self.tableViewChanged = False
                
    
    def keyPressEvent(self, event):
        '''
        Handles key presses anywhere in the program.
        '''
        
        if event.key() in forwardKeys:
            self.nextImage()
        if event.key() in backwardKeys:
            self.prevImage()
        if event.key() == Qt.Key_Backspace:
            self.coordList.removeLastPoint()
        if event.key() == Qt.Key_Delete:
            if not self.ignoreDeletes:
                self.table.deleteSelectedRows()
            self.ignoreDeletes = False   
        if event.key() == Qt.Key_W:
            self.shiftSelected('up')
        if event.key() == Qt.Key_A:
            self.shiftSelected('left')
        if event.key() == Qt.Key_S:
            self.shiftSelected('down')
        if event.key() == Qt.Key_D:
            self.shiftSelected('right')
        self.tableViewChanged = True

        
    def initUI(self):
        '''
        Initialises the UI layout and widgets.
        '''
        
        mainBox = QtGui.QHBoxLayout()
        
        imageBox = QtGui.QVBoxLayout()
        outputBox = QtGui.QVBoxLayout()
        titleBox = QtGui.QHBoxLayout()
        
        self.imagePathLabel = QtGui.QLabel("", self)
        self.imageLabel = QtGui.QLabel("No image loaded.", self)
        self.image = QtGui.QPixmap()

        self.imageBlockScene = ClickableImageBox(parent = self)
        self.imageBlockScene.addPixmap(self.image)

        self.imageBlock = QtGui.QGraphicsView()
        self.imageBlock.setScene(self.imageBlockScene)
        self.imageBlock.setMinimumWidth(imageColumnMinWidth)
        
        folderButton = QtGui.QPushButton("Image folder:")
        folderButton.setMaximumWidth(180)
        folderButton.clicked.connect(self.selectFolder)

        tableCopyButton = QtGui.QPushButton("Copy")
        tableCopyButton.setMinimumWidth(40)
        tableCopyButton.clicked.connect(self.copyTable)

        tableExportButton = QtGui.QPushButton("Export")
        tableExportButton.setMinimumWidth(40)
        tableExportButton.clicked.connect(self.exportTable)

        tableClearButton = QtGui.QPushButton("Clear")
        tableClearButton.setMinimumWidth(40)
        tableClearButton.clicked.connect(self.clearTable)
        
        self.table = TableBox(0,2)
        self.table.toolScreen = self
        self.table.setHorizontalHeaderLabels(['x','y'])
        self.table.setSelectionBehavior(QtGui.QTableWidget.SelectRows)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.table.setMinimumWidth(outputColumnMinWidth)
        self.table.setMaximumWidth(outputColumnMaxWidth)
        self.table.setMinimumHeight(outputColumnMinHeight)
        
        self.listBlock = QtGui.QListWidget()
        self.listBlock.setMinimumWidth(outputColumnMinWidth)
        self.listBlock.setMaximumWidth(outputColumnMaxWidth)
        self.listBlock.setMinimumHeight(outputColumnMinHeight)
        self.listBlock.currentRowChanged.connect(self.changeImageFromList)
       
        titleBox.addWidget(folderButton)
        titleBox.addWidget(self.imagePathLabel)
        titleBox.addWidget(self.imageLabel)
        imageBox.addWidget(self.imageBlock)
        imageBox.addLayout(titleBox)
        
        outputBox.addWidget(self.table)
        
        tableButtonsLayout = QtGui.QHBoxLayout()
        tableButtonsLayout.addWidget(tableCopyButton)
        tableButtonsLayout.addWidget(tableExportButton)
        tableButtonsLayout.addWidget(tableClearButton)
        tableLayout = QtGui.QVBoxLayout()   
        tableLayout.addLayout(tableButtonsLayout)     
        tableLayout.addWidget(self.table)
        tableWidget = QtGui.QWidget()
        tableWidget.setLayout(tableLayout)

        outputBoxSplitter = QtGui.QSplitter(Qt.Vertical)
        outputBoxSplitter.addWidget(tableWidget)
        outputBoxSplitter.addWidget(self.listBlock)
        outputBoxSplitter.setChildrenCollapsible(False)
        outputBoxSplitter.setStretchFactor(0, 3)
        outputBoxSplitter.setStretchFactor(1, 1)
        
        imageBoxWidget = QtGui.QWidget()
        imageBoxWidget.setLayout(imageBox)
        
        mainBoxSplitter = QtGui.QSplitter(Qt.Horizontal)
        mainBoxSplitter.setChildrenCollapsible(False)
        mainBoxSplitter.addWidget(imageBoxWidget)
        mainBoxSplitter.addWidget(outputBoxSplitter)
        mainBoxSplitter.setStretchFactor(0, 4)
        mainBoxSplitter.setStretchFactor(1, 1)
                
        mainBox.addWidget(mainBoxSplitter)
        
        self.setLayout(mainBox)
        
        self.setWindowTitle('Quick Coords')
        self.setWindowState(Qt.WindowMaximized)
    
        self.show()


    def selectFolder(self):
        '''
        Brings up a folder selection dialog and sets the current path to the selcted folder.
        '''
        
        fileDialog = QtGui.QFileDialog()
        newPath = fileDialog.getExistingDirectory(self, "Select a folder with images", self.imagePath)
        self.setFoldertoPath(newPath)

        
    def setFoldertoPath(self, newPath):
        '''
        Handles a change in path. Checks that the path exists, fills the list box, loads the first image, and saves the current folder.
        '''
        
        if len(newPath) > 0 and os.access(newPath, 0):
            self.imagePath = newPath.replace('\\','/').rstrip('/')+'/' # Replace Windows' stupid file separator with one that works on all platforms.
            self.imagePathLabel.setText(self.imagePath)
            fileList = os.listdir(self.imagePath)
            fileList.sort()
            self.imageList = []
            for i in fileList:
                extension = i.split('.')[-1]
                if extension in supportedExtensions:
                    self.imageList.append(self.imagePath + i)
            self.currentImageNum = 0
        
            self.setImage()
            self.fillListBox()
            self.saveCurrentFolder()
        
    
    def copyTable(self):
        '''
        Copies a tab separated list to the clipboard, suitable for pasting into most spreadsheet programs
        '''
        
        self.clipboard.setText(self.coordList.copyAsText())


    def exportTable(self):
        '''
        Saves a CSV or plain text file containg a comma separated list of points.
        '''
        
        fileDialog = QtGui.QFileDialog()
        filters = 'CSV files (*.csv);;Text files (*.txt);;All files (*.*)'
        exportLocation = fileDialog.getSaveFileName(self, "Choose file to export to", self.imagePath, filter=filters)
        
        exportFile = open(exportLocation, 'w')
        exportFile.write(self.coordList.copyAsCSV())
        exportFile.close()
        

    def clearTable(self):
        '''
        Deletes all points.
        '''
        
        self.coordList.clear()
        self.tableViewChanged = True

    
    def fillListBox(self):
        '''
        Fills the list box with the names of the images in the folder.
        Note: Does not check if images have been added since the folder was loaded. To do this, reset the folder.
        '''
        
        self.listBlock.clear()
        if len(self.imageList) > 0:
            for f in self.imageList:
                thisImage = f.split('/')[-1]
                self.listBlock.addItem(thisImage)
            self.listBlock.setCurrentRow(self.currentImageNum)
        else:
            print("No images in current folder")
        self.tableViewChanged = True

        
    def changeImageFromList(self):
        '''
        Changes the image to the currently selected image in the list.
        '''
        
        self.currentImageNum = self.listBlock.currentRow()
        self.setImage()
    

    def shiftSelected(self, direction):
        '''
        Moves the selected points 1 pixel (on the screen, not on the image) in the specified direction.
        Direction can be 'up', 'down', 'left' or 'right'.
        '''
        
        selectedPoints = self.table.getSelectedPoints()
        for i in selectedPoints:
            self.coordList.points[i].shift(direction, 1.0/imageScaleFactor)
        

    def setImage(self):
        '''
        Loads the current image from disk and sets it for display.
        '''
        
        if len(self.imageList) > 0:
            currentImage = self.imageList[self.currentImageNum]
            print("Attempting to load Current image",currentImage)
            self.image = QtGui.QPixmap(currentImage)
            self.image.originalWidth = self.image.width()
            self.image.originalHeight = self.image.height()
            width = self.image.originalWidth * self.scaleFactor
            height = self.image.originalHeight * self.scaleFactor
            self.image = self.image.scaled(width, height, Qt.KeepAspectRatio)
            self.originalImage = self.image.copy()
            self.imageBlockScene.clear()
            self.imageBlockScene.setSceneRect(0, 0, width, height) 
            self.imageBlockScene.addPixmap(self.image)
            self.imageLabel.setText(currentImage.split('/')[-1])
            self.listBlock.setCurrentRow(self.currentImageNum)
        else:
            print("No images in current folder")
        
        
    def updatePoints(self):
        '''
        Updates the table to reflect the current state of the coordinate list.
        '''

        selectedPoints = self.table.getSelectedPoints()
        points = self.coordList.points
        nPoints = len(points)
        self.table.clearContents()
        self.table.setRowCount(nPoints)
        for i in range(nPoints):
            xItem = QtGui.QTableWidgetItem('{:.1f}'.format(points[i].x))
            xItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 0, xItem)
            yItem = QtGui.QTableWidgetItem('{:.1f}'.format(points[i].y))
            yItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 1, yItem)
        self.table.setSelectedRows(selectedPoints)
        
            
    def drawImagePoints(self):
        '''
        Redraws the points on the display.
        '''
        
        # We don't want to actually draw the points onto the image, because then we'd have to reload the
        # image from disk to undo the changes. Instead, we work on a copy, and only display the copy.
        # The original image remains unchanged in memory.
        newImage = self.originalImage.toImage()
        
        for p in self.coordList.points:
            top = int((p.y-0.4) * self.scaleFactor)
            bottom = int((p.y+0.4) * self.scaleFactor)
            left = int((p.x-0.4) * self.scaleFactor)
            right = int((p.x+0.4) * self.scaleFactor)
            if p.colour == 0:
                colour = QtGui.qRgb(0, 255, 0)
            else:
                colour = QtGui.qRgb(255, 0, 0)
            borderColour = QtGui.qRgb(0, 0, 0)
            for x in range(left, right+1):
                for y in range(top, bottom+1):    
                    newImage.setPixel(x, y, colour)
            for x in range(left-1, right+2):
                for y in [top-1, bottom+1]:    
                    newImage.setPixel(x, y, borderColour)
            for x in [left-1, right+1]:
                for y in range(top-1, bottom+2):    
                    newImage.setPixel(x, y, borderColour)
            
        self.image.convertFromImage(newImage)
        self.imageBlockScene.update()
 
    
    def nextImage(self):
        '''
        Changes to the next image.
        '''
        
        self.currentImageNum += 1
        if self.currentImageNum >= len(self.imageList):
            self.currentImageNum = 0
        self.setImage()
            
                   
    def prevImage(self):
        '''
        Changes to the previous image.
        '''
        
        self.currentImageNum -= 1
        if self.currentImageNum < 0:
            self.currentImageNum = len(self.imageList)-1
        self.setImage()
            
                
    def saveCurrentFolder(self):
        '''
        Saves the current folder to a file, allowing the folder selection to be persistant if the program is exited.
        '''
        
        try:
            folderFile = open(folderSaveFileName, 'w')
            folderFile.write(self.imagePath)
            folderFile.close()
        except IOError:
            print("Could not save last folder")
            
        
    def loadLastFolder(self):
        '''
        Loads the last current folder from disk.
        '''
        
        try:
            folderFile = open(folderSaveFileName, 'r')
            path = folderFile.readline().strip()
            if len(path) > 0 and os.access(path, 0):
                self.imagePath = path
            folderFile.close()
        except IOError:
            print("Could not load last folder")
            self.imagePath = ""
        
                                      
def main():
    
    app = QtGui.QApplication(sys.argv)
    toolScreen = ToolScreen() #@UnusedVariable used to prevent prevent premature garbage collection
    toolScreen.clipboard = app.clipboard()
    print("!!!")
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
