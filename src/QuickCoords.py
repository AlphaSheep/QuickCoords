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

outputColumnMinWidth = 160
outputColumnMaxWidth = 640
outputColumnMinHeight = 160

folderSaveFileName = 'lastfolder.txt'

targetFPS = 30


#===================#
# Class definitions # 
#===================#


class Point():
    
    def __init__(self, x, y):
        
        self.x = x
        self.y = y
        self.colour = 0
        
    
    def shift(self, direction, amount):
        
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
    
    def __init__(self, initPoints):
        
        self.points = initPoints
        from time import time
        self.id = time()


    def addPoint(self, point):
        
        self.points.append(point)
        
    
    def addPoints(self, points):
        
        for p in points:
            self.points.append(p)
            
            
    def removeLastPoint(self):
        
        self.points = self.points[:-1]
    
    
    def length(self):
        
        return len(self.points)
    
    
    def removePoint(self, n):
        
        if n >= len(self.points):
            self.points[n] # Lazily force list index out of range, otherwise it would have passed silently.
        else:
            self.points = self.points[:n] + self.points[n+1:]
        

    def __str__(self):
         
        res = ''
        for p in self.points:
            res += str(p)+' '
        return res.strip()


class ClickableImageBox(QtGui.QGraphicsScene):
    
    def mouseReleaseEvent(self, *args, **kwargs):
        
        event = args[0]
        if event.button() == Qt.LeftButton:
            point = Point(event.scenePos().x()/imageScaleFactor, event.scenePos().y()/imageScaleFactor)
            self.parent().coordList.addPoint(point)
            #self.parent().updatePoints()
        if event.button() == Qt.RightButton:
            self.parent().coordList.removeLastPoint()
            #self.parent().updatePoints()

        return QtGui.QGraphicsScene.mouseReleaseEvent(self, *args, **kwargs)


class TableBox(QtGui.QTableWidget):
    
    def keyPressEvent(self, *args, **kwargs):
        
        event = args[0]
        if event.key() == Qt.Key_Delete:
            self.deleteSelectedRows()
        self.toolScreen.keyPressEvent(event)
        
        return QtGui.QTableWidget.keyPressEvent(self, *args, **kwargs)
    
    
    def deleteSelectedRows(self):
        
        newCoordList = CoordinateList([])
        oldCoordList = self.toolScreen.coordList

        selectedPoints = self.getSelectedPoints()
        
        for i in range(self.rowCount()):
            if not i in selectedPoints:
                newCoordList.addPoint(oldCoordList.points[i])
        self.toolScreen.coordList = newCoordList
        # self.toolScreen.updatePoints()
        
    
    def selectionChanged(self, *args, **kwargs):
        
        selectedPoints = self.getSelectedPoints()
        
        for i in range(self.toolScreen.coordList.length()):
            # print(i, self.rowCount(), len(self.toolScreen.coordList.points))
            if i in selectedPoints:
                self.toolScreen.coordList.points[i].colour = 1
            else:
                self.toolScreen.coordList.points[i].colour = 0
                
        return QtGui.QTableWidget.selectionChanged(self, *args, **kwargs)
    
    
    def getSelectedPoints(self):
        
        selectedPoints = []
        for index in self.selectionModel().selectedRows():
            selectedPoints.append(index.row())
        return selectedPoints
            
        
    def setSelectedRows(self, rows):
        
        selectedItems = self.selectionModel().selection()
        for i in rows:      
            self.selectRow(i)      
            selectedItems.merge(self.selectionModel().selection(), QtGui.QItemSelectionModel.Select)
        self.clearSelection()
        self.selectionModel().select(selectedItems, QtGui.QItemSelectionModel.Select)



class ToolScreen(QtGui.QWidget):
    
    def __init__(self):

        super(ToolScreen, self).__init__() # Call the constructor of this class's parent        
        self.prepare()
        self.initUI()
        self.setFoldertoPath(self.imagePath)

        self.fpsTimer = QTimer()
        self.fpsTimer.timeout.connect(self.updateDisplay)
        self.fpsTimer.start(1000/targetFPS)


    def prepare(self):

        self.loadLastFolder()
        self.currentImageNum = 0
        self.imageList = []
        self.coordList = CoordinateList([])
        self.scaleFactor = imageScaleFactor
               
                     
    def updateDisplay(self):
        
        self.updatePoints()
        self.drawImagePoints()
                
    
    def keyPressEvent(self, event):
        
        if event.key() in forwardKeys:
            self.nextImage()
        if event.key() in backwardKeys:
            self.prevImage()
        if event.key() == Qt.Key_Backspace:
            self.coordList.removeLastPoint()
        if event.key() == Qt.Key_W:
            self.shiftSelected('up')
        if event.key() == Qt.Key_A:
            self.shiftSelected('left')
        if event.key() == Qt.Key_S:
            self.shiftSelected('down')
        if event.key() == Qt.Key_D:
            self.shiftSelected('right')

        
    def initUI(self):
        
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
        self.imageBlock.setMinimumWidth(240)
        
        folderButton = QtGui.QPushButton("Image folder:")
        folderButton.setMaximumWidth(80)
        folderButton.clicked.connect(self.selectFolder)
        
        #self.editBlock = QtGui.QTextEdit()
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
        
        outputBoxSplitter = QtGui.QSplitter(Qt.Vertical)
        outputBoxSplitter.addWidget(self.table)
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
        
        fileDialog = QtGui.QFileDialog()
        newPath = fileDialog.getExistingDirectory(None, "Select a folder with images", self.imagePath)
        self.setFoldertoPath(newPath)

        
    def setFoldertoPath(self, newPath):
        
        if len(newPath) > 0 and os.access(newPath, 0):
            self.imagePath = newPath.replace('\\','/').strip('/')+'/' # Replace Windows' stupid file seperator with one that works on all platforms.
            self.imagePathLabel.setText(self.imagePath)
            fileList = os.listdir(self.imagePath)
            self.imageList = []
            for i in fileList:
                extension = i.split('.')[-1]
                if extension in supportedExtensions:
                    self.imageList.append(self.imagePath + i)
            self.currentImageNum = 0
            #print (self.imageList)
        
            self.setImage()
            self.fillListBox()
            self.saveCurrentFolder()
        
    
    def fillListBox(self):
        
        self.listBlock.clear()
        if len(self.imageList) > 0:
            for f in self.imageList:
                thisImage = f.split('/')[-1]
                self.listBlock.addItem(thisImage)
            self.listBlock.setCurrentRow(self.currentImageNum)
        else:
            print("No images in current folder")
        
    
    def changeImageFromList(self):
        
        self.currentImageNum = self.listBlock.currentRow()
        self.setImage()
    

    def shiftSelected(self, direction):
        
        selectedPoints = self.table.getSelectedPoints()
        for i in selectedPoints:
            self.coordList.points[i].shift(direction, 1.0/imageScaleFactor)
        

    def setImage(self):
        
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
            #self.imageBlock.setPixmap(self.image)
            self.imageLabel.setText(currentImage.split('/')[-1])
            self.listBlock.setCurrentRow(self.currentImageNum)
            #self.updatePoints()
        else:
            print("No images in current folder")
        
        
    def updatePoints(self):

        selectedPoints = self.table.getSelectedPoints()
        print(selectedPoints)
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
        
        self.currentImageNum += 1
        if self.currentImageNum >= len(self.imageList):
            self.currentImageNum = 0
        self.setImage()
            
                   
    def prevImage(self):
        
        self.currentImageNum -= 1
        if self.currentImageNum < 0:
            self.currentImageNum = len(self.imageList)-1
        self.setImage()
            
                
    def saveCurrentFolder(self):
        
        try:
            folderFile = open(folderSaveFileName, 'w')
            folderFile.write(self.imagePath)
            folderFile.close()
        except IOError:
            print("Could not save last folder")
            
        
    def loadLastFolder(self):
        
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
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
