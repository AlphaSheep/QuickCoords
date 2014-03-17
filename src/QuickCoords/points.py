'''
QuickCoords/points.py

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

This module provides the Point and CoordinateList classes.

'''


from QuickCoords.constants import selectionRadius



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

