'''
Created on 05 Mar 2014

@author: AlphanumericSheepPig
'''

import sys, os#, shutil

from PyQt4.QtCore import Qt
from PyQt4 import QtGui

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

        self.imageBlock = QtGui.QLabel(self) # Just a dummy label to hold an image
        self.imageLabel = QtGui.QLabel(self.imagePath, self)
        folderButton = QtGui.QPushButton("Image folder:")
        folderButton.clicked.connect(self.selectFolder)
        
        editBlock = QtGui.QTextEdit()
       
        titleBox.addWidget(folderButton)
        titleBox.addWidget(self.imageLabel)
        imageBox.addLayout(titleBox)
        imageBox.addWidget(self.imageBlock)
        imageBox.addStretch(1)
        
        outputBox.addWidget(editBlock)
        
        mainBox.addLayout(imageBox)
        mainBox.addStretch(1)
        mainBox.addLayout(outputBox)
        
        self.setLayout(mainBox)
        
        self.setWindowTitle('Quick Coords')
        self.setWindowState(Qt.WindowMaximized)
    
        self.show()


    def selectFolder(self):
        
        self.imagePath = QtGui.QFileDialog.getExistingDirectory(self, "Select a folder with images")
        self.imageLabel.setText(self.imagePath)
        
        
    
        
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    toolScreen = ToolScreen()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
