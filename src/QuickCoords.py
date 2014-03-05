'''
Created on 05 Mar 2014

@author: AlphanumericSheepPig
'''

import sys, os#, shutil

from PyQt4.QtCore import Qt
from PyQt4 import QtGui


supportedExtensions = ['png', 'jpg', 'jpeg', 'bmp', 'gif']


class ToolScreen(QtGui.QWidget):
    
    def __init__(self):
        super(ToolScreen, self).__init__() # Call the constructor of this class's parent        
        self.initUI()
        
    def initUI(self):
        
        mainBox = QtGui.QHBoxLayout()
        
        imageBox = QtGui.QVBoxLayout()
        outputBox = QtGui.QVBoxLayout()
        titleBox = QtGui.QHBoxLayout()
        
        self.imagePath = ""

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


    def selectFolder(self):
        
        self.imagePath = QtGui.QFileDialog.getExistingDirectory(self, "Select a folder with images", self.imagePath)+'/'
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
        currentImage = self.imageList[self.currentImageNum]
        print("Attempting to load Current image",currentImage)
        self.image = QtGui.QPixmap(currentImage)
        self.imageBlock.setPixmap(self.image)
        self.imageLabel.setText(currentImage.split('/')[-1])
        
    
        
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    toolScreen = ToolScreen()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
