'''
QuickCoords/main.py

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

This module provides the ToolScreen class.

'''

import os

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QTimer

from QuickCoords.constants import supportedExtensions, imageScaleFactor, folderSaveFileName,\
                                  imageColumnMinWidth, outputColumnMinWidth, outputColumnMaxWidth,\
                                  outputColumnMinHeight, targetFPS, forwardKeys,\
                                  backwardKeys
from QuickCoords.image import ClickableImageBox
from QuickCoords.points import CoordinateList
from QuickCoords.table import TableBox


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
                    if x>0 and x<newImage.width() and y>0 and y<newImage.height():    
                        newImage.setPixel(x, y, colour)
            for x in range(left-1, right+2):
                for y in [top-1, bottom+1]:    
                    if x>0 and x<newImage.width() and y>0 and y<newImage.height():    
                        newImage.setPixel(x, y, borderColour)
            for x in [left-1, right+1]:
                for y in range(top-1, bottom+2):    
                    if x>0 and x<newImage.width() and y>0 and y<newImage.height():    
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
        
