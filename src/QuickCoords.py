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

from PyQt4.QtCore import Qt
from PyQt4 import QtGui


#==================#
# Global constants #
#==================#

supportedExtensions = ['png', 'jpg', 'jpeg', 'bmp', 'gif']

forwardKeys = [Qt.Key_Greater, Qt.Key_Period, Qt.Key_D, Qt.Key_K, Qt.Key_Plus, Qt.Key_Equal]
backwardKeys = [Qt.Key_Less, Qt.Key_Comma, Qt.Key_A, Qt.Key_J, Qt.Key_Minus]

imageScaleFactor = 6

folderSaveFileName = 'lastfolder.txt'


#===================#
# Class definitions # 
#===================#


class Point():
    
    def __init__(self, x, y):
        
        self.x = x
        self.y = y
        
        
    def __repr__(self):
        
        return '('+str(self.x)+', '+str(self.y)+')'


class CoordinateList():
    
    def __init__(self, points = []):
        
        self.points = points


    def addPoint(self, point):
        
        self.points.append(point)
        
    
    def addPoints(self, points):
        
        for p in points:
            self.points.append(p)
            
            
    def removeLastPoint(self):
        
        self.points = self.points[:-1]
    
    
    def removePoint(self, n):
        
        if n >= len(self.points):
            self.points[n] # Lazily force list index out of range, otherwise it would have passed silently.
        else:
            self.points = self.points[:n] + self.points[n+1:]
        

    def __repr__(self):
        
        res = ''
        for p in self.points:
            res += str(p)+' '
        return res.strip()


class ClickableImageBox(QtGui.QGraphicsScene):
    
    def mouseReleaseEvent(self, *args, **kwargs):
        
        event = args[0]
        if event.button() == Qt.LeftButton:
            point = Point(event.scenePos().x()/imageScaleFactor, event.scenePos().y()/imageScaleFactor)
            print(point)
            self.parent().coordList.addPoint(point)
            self.parent().updatePoints()

        return QtGui.QGraphicsScene.mouseReleaseEvent(self, *args, **kwargs)


class TableBox(QtGui.QTableWidget):
    
    def keyPressEvent(self, *args, **kwargs):
        
        event = args[0]
        print("Pressed a key in the table", event.key())
        
        return QtGui.QTableWidget.keyPressEvent(self, *args, **kwargs)
    
        

class ToolScreen(QtGui.QWidget):
    
    def __init__(self):

        super(ToolScreen, self).__init__() # Call the constructor of this class's parent        
        self.prepare()
        self.initUI()
        self.setFoldertoPath(self.imagePath)


    def prepare(self):

        self.loadLastFolder()
        self.currentImageNum = 0
        self.imageList = []
        self.coordList = CoordinateList()
        self.scaleFactor = imageScaleFactor
        
    
    def keyPressEvent(self, event):
        
        if event.key() in forwardKeys:
            self.nextImage()
        if event.key() in backwardKeys:
            self.prevImage()
        
        
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
        self.table = TableBox(0,2, parent = self)
        self.table.setHorizontalHeaderLabels(['x','y'])
        self.table.setSelectionBehavior(QtGui.QTableWidget.SelectRows)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.table.setMinimumWidth(160)
        self.table.setMaximumWidth(240)
        self.table.setMinimumHeight(160)
        
        self.listBlock = QtGui.QListWidget()
        self.listBlock.setMinimumWidth(160)
        self.listBlock.setMaximumWidth(240)
        self.listBlock.setMinimumHeight(160)
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
        
        #imageBoxWidget = QtGui.QWidget()
        #imageBoxWidget.setLayout(imageBox)
        #outputBoxWidget = QtGui.QWidget()
        #outputBoxWidget.setLayout(outputBox)
        
        mainBox.addLayout(imageBox)
        mainBox.addWidget(outputBoxSplitter)
        
        #mainBox.addWidget(mainBoxSplitter)
        
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
    

    def setImage(self):
        
        if len(self.imageList) > 0:
            currentImage = self.imageList[self.currentImageNum]
            print("Attempting to load Current image",currentImage)
            self.image = QtGui.QPixmap(currentImage)
            width = self.image.width()*self.scaleFactor
            height = self.image.height()*self.scaleFactor
            self.image = self.image.scaled(width, height, Qt.KeepAspectRatio)
            self.imageBlockScene.clear()
            self.imageBlockScene.setSceneRect(0, 0, width, height) 
            self.imageBlockScene.addPixmap(self.image)
            #self.imageBlock.setPixmap(self.image)
            self.imageLabel.setText(currentImage.split('/')[-1])
            self.listBlock.setCurrentRow(self.currentImageNum)
        else:
            print("No images in current folder")
        
        
    def updatePoints(self):
        
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
            
            
            
            
    
    def dragImage(self, dx, dy):
        
        print ("Dragging image",self.imageBlock.width(),self.imageBlock.height())
        self.imageBlock.scroll(-dx, -dy)
        
    
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
    toolScreen = ToolScreen() 
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
