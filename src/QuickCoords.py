'''
Created on 05 Mar 2014

@author: AlphanumericSheepPig
'''

import sys, os#, shutil

from PyQt4.QtCore import Qt, QEvent
from PyQt4 import QtGui


#===========#
# Constants #
#===========#

supportedExtensions = ['png', 'jpg', 'jpeg', 'bmp', 'gif']

forwardKeys = [Qt.Key_Greater, Qt.Key_Period, Qt.Key_D, Qt.Key_K, Qt.Key_Plus, Qt.Key_Equal]
backwardKeys = [Qt.Key_Less, Qt.Key_Comma, Qt.Key_A, Qt.Key_J, Qt.Key_Minus]

dragTolerance = 16 

folderSaveFileName = 'lastfolder.txt'


#===================#
# Class definitions # 
#===================#

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
        self.scaleFactor = 6
        
    
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

        self.imageBlockScene = QtGui.QGraphicsScene()
        self.imageBlockScene.addPixmap(self.image)

        self.imageBlock = QtGui.QGraphicsView()
        self.imageBlock.setScene(self.imageBlockScene)
        self.imageBlock.setMinimumWidth(240)
        
        folderButton = QtGui.QPushButton("Image folder:")
        folderButton.setMaximumWidth(80)
        folderButton.clicked.connect(self.selectFolder)
        
        #self.editBlock = QtGui.QTextEdit()
        self.editBlock = QtGui.QTableWidget(0,2)
        self.editBlock.setHorizontalHeaderLabels(['x','y'])
        self.editBlock.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.editBlock.setMinimumWidth(160)
        self.editBlock.setMaximumWidth(240)
        self.editBlock.setMinimumHeight(160)
        
        self.listBlock = QtGui.QListWidget()
        self.listBlock.setMinimumWidth(160)
        self.listBlock.setMaximumWidth(240)
        self.listBlock.setMinimumHeight(160)
        self.listBlock.currentRowChanged.connect(self.changeImageFromList)
       
        titleBox.addWidget(folderButton)
        titleBox.addWidget(self.imagePathLabel)
        imageBox.addLayout(titleBox)
        imageBox.addWidget(self.imageBlock)
        imageBox.addWidget(self.imageLabel)
        
        outputBox.addWidget(self.editBlock)
        
        outputBoxSplitter = QtGui.QSplitter(Qt.Vertical)
        outputBoxSplitter.addWidget(self.editBlock)
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
        
        newPath = QtGui.QFileDialog.getExistingDirectory(self, "Select a folder with images", self.imagePath)
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
        
        
    def getImageCoord(self, x, y):
        
        print("Getting coord", x, y)
        
    
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
