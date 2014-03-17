'''
QuickCoords/constants.py

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

This module defines some global constants.

'''


from PyQt4.QtCore import Qt


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