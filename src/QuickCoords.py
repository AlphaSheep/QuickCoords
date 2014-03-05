'''
Created on 05 Mar 2014

@author: AlphanumericSheepPig
'''

import sys, os#, shutil

from PyQt4.QtCore import Qt, QEvent
from PyQt4 import QtGui


supportedExtensions = ['png', 'jpg', 'jpeg', 'bmp', 'gif']

forwardKeys = [Qt.Key_Greater, Qt.Key_Period, Qt.Key_D, Qt.Key_K, Qt.Key_Plus]
backwardKeys = [Qt.Key_Less, Qt.Key_Comma, Qt.Key_A, Qt.Key_J, Qt.Key_Minus]



class ToolScreen(QtGui.QWidget):
    
    def __init__(self):

        super(ToolScreen, self).__init__() # Call the constructor of this class's parent        
        self.prepare()
        self.initUI()
        self.installEventFilter(self)


    def prepare(self):

        self.imagePath = ""
        self.currentImageNum = 0
        self.imageList = []
        
        
    def initUI(self):
        
        mainBox = QtGui.QHBoxLayout()
        
        imageBox = QtGui.QVBoxLayout()
        outputBox = QtGui.QVBoxLayout()
        titleBox = QtGui.QHBoxLayout()
        
        self.imagePathLabel = QtGui.QLabel("", self)
        self.imageLabel = QtGui.QLabel("No image loaded.", self)
        self.image = QtGui.QPixmap()
        self.imageBlock = QtGui.QLabel(self) # Just a dummy label to hold the image
        self.imageBlock.setPixmap(self.image)
        
        folderButton = QtGui.QPushButton("Image folder:")
        folderButton.clicked.connect(self.selectFolder)
        
        editBlock = QtGui.QTextEdit()
       
        titleBox.addWidget(folderButton)
        titleBox.addWidget(self.imagePathLabel)
        imageBox.addLayout(titleBox)
        imageBox.addWidget(self.imageBlock)
        imageBox.addStretch(1)
        imageBox.addWidget(self.imageLabel)
        
        outputBox.addWidget(editBlock)
        
        mainBox.addLayout(imageBox)
        mainBox.addStretch(1)
        mainBox.addLayout(outputBox)
        
        self.setLayout(mainBox)
        
        self.setWindowTitle('Quick Coords')
        self.setWindowState(Qt.WindowMaximized)
    
        self.show()


    def eventFilter(self, obj, event):
        
        if event.type() == QEvent.KeyPress:
            print ("pressed something")
            if event.key() in forwardKeys:
                self.nextImage()
            if event.key() in backwardKeys:
                self.prevImage()
        return super(ToolScreen, self).eventFilter(obj, event)
     

    def selectFolder(self):
        
        newPath = QtGui.QFileDialog.getExistingDirectory(self, "Select a folder with images", self.imagePath)
        if len(newPath)>0:
            self.imagePath = newPath+'/'
            self.imagePathLabel.setText(self.imagePath)
            fileList = os.listdir(self.imagePath)
            self.imageList = []
            for i in fileList:
                extension = i.split('.')[-1]
                if extension in supportedExtensions:
                    self.imageList.append(self.imagePath + i)
                    self.imageList[-1].replace('\\','/') # Replace Windows' stupid file seperator with one that works on all platforms.
            self.currentImageNum = 0
            print (self.imageList)
        
            self.setImage()
        

    def setImage(self):
        
        if len(self.imageList) > 0:
            currentImage = self.imageList[self.currentImageNum]
            print("Attempting to load Current image",currentImage)
            self.image = QtGui.QPixmap(currentImage)
            self.imageBlock.setPixmap(self.image)
            self.imageLabel.setText(currentImage.split('/')[-1])
        else:
            print("No images in current folder")
        
        
        
    
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
            
                              
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    toolScreen = ToolScreen()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
