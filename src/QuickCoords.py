'''
Created on 05 Mar 2014

@author: AlphanumericSheepPig
'''

import sys

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
        
        imagePath = QtGui.QFileDialog.getExistingDirectory(self, "Select a folder with images")

        imageBlock = QtGui.QLabel(self) # Just a dummy label to hold an image
        imageLabel = QtGui.QLabel(imagePath, self)
        
        editBlock = QtGui.QTextEdit()
        
       
        imageBox.addWidget(imageLabel)
        imageBox.addWidget(imageBlock)
        
        mainBox.addLayout(imageBox)
        mainBox.addLayout(outputBox)
        
        
        self.setLayout(mainBox)
        
        screenGeometry = QtGui.QDesktopWidget().availableGeometry()
        self.setWindowTitle('Quick Coords')
        self.setWindowState(Qt.WindowMaximized)
    
        self.show()

        
def main():
    
    app = QtGui.QApplication(sys.argv)
    toolScreen = ToolScreen()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()
