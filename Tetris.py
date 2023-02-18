from tkinter import X
from PyQt5 import QtGui
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QBrush, QPen, QFont
from PyQt5.QtCore import Qt
import sys
from PyQt5.QtWidgets import QLabel
import numpy as np
import random
import time
import threading
import pygame
KEY_LEFT = 16777234
KEY_RIGHT = 16777236
KEY_UP = 16777235
KEY_DOWN = 16777237
KEY_ROTATE = KEY_UP
KEY_P = 80
KEY_S = 83
GridSize = 40

class SpeedDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speed Dialog")
        self.width = 1500
        self.height = 300
        self.layout = QGridLayout()
        self.setStyleSheet("background-color: gray")
        self.sl = QtWidgets.QSlider(Qt.Horizontal)
        self.sl.setMinimum(100)
        self.sl.setMaximum(1000)
        self.sl.setValue(500)
        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.setTickInterval(200)
        self.sl.setStyleSheet(self.styleSheet1())
        self.layout.addWidget(self.sl, 0, 0, 1, 10)
        self.sl.valueChanged.connect(self.valueChange)
        self.label1 = QLabel("Easy")
        self.label1.setStyleSheet(self.styleSheet2())
        self.label2 = QLabel("Hard")
        self.label2.setStyleSheet(self.styleSheet2())
        self.layout.addWidget(self.label2, 1, 0)
        self.layout.addWidget(self.label1, 1, 9)
        self.setLayout(self.layout)
    def valueChange(self):
        return self.sl.value()
    

    def styleSheet1(self):
        return"""
        QSlider{
        background-color:'blue';
        padding:1px;  
        }
        """

    def styleSheet2(self):
        return"""
        QLabel{
        background-color:'lightblue';
        color:white;
        padding:1px;
        min-width:20px;
        qproperty-alignment:'AlignCenter|AlignRight';   
        }
        """

class TObject():
    def __init__(self, type, max_x, max_y):
        self.type = type
        self.max_x = max_x
        self.max_y = max_y
        self.cells = np.zeros((4, 2), dtype=np.int8)
        self.define_object(type)

    def define_object(self, type):
        self.type = type
        self.center = 0
        if self.type == 0:
            self.cells[0, :] = 0, 0
            self.cells[1, :] = 1, 0
            self.cells[2, :] = 2, 0
            self.cells[3, :] = 3, 0
            self.center = 1
        if self.type == 1:
            self.cells[0,:] = 0, 0
            self.cells[1,:] = 1, 0
            self.cells[2,:] = 1, 1
            self.cells[3,:] = 0, 1
            self.center = 0
        if self.type == 2:
            self.cells[0,:] = 0, 0
            self.cells[1,:] = 1, 0
            self.cells[2,:] = 1, 1
            self.cells[3,:] = 1, 2
            self.center = 1
        if self.type == 3:
            self.cells[0,:] = 0, 0
            self.cells[1,:] = 1, 0
            self.cells[2,:] = 1, 1
            self.cells[3,:] = 2, 1
            self.center = 2
        if self.type == 4:
            self.cells[0,:] = 0, 0
            self.cells[1,:] = 1, 0
            self.cells[2,:] = 1, 1
            self.cells[3,:] = 2, 0
            self.center = 1
        if self.type == 5:
            self.cells[0,:] = 0, 0
            self.cells[1,:] = 0, 1
            self.cells[2,:] = 1, 1
            self.cells[3,:] = 2, 1
        if self.type == 6:
            self.cells[0,:] = 0, 1
            self.cells[1,:] = 1, 1
            self.cells[2,:] = 1, 0
            self.cells[3,:] = 2, 0
    
    def re_init(self, type):
        self.define_object(type)

    def rotate(self, map):
        flag =  True
        tmp_results = self.cells.copy()
        for ic in range(4):
            cx, cy = self.cells[self.center, :]
            x, y = self.cells[ic, :]
            tmp_results[ic, 0] = -y + cy + cx
            tmp_results[ic, 1] = -cx + x + cy
            if tmp_results[ic, 0] < 0 or tmp_results[ic, 0] > self.max_x:
                flag = False
                break
            if tmp_results[ic, 1] < 0 or tmp_results[ic, 1] > self.max_y:
                flag = False
                break
            if map[tmp_results[ic, 1], tmp_results[ic, 0]] == 1:
                flag = False
                break

        if flag == True:
            self.cells = tmp_results.copy()
                
    def move(self, deltax, deltay, map):

        flag = True
        for i in range(4):
            x = self.cells[i, 0] + deltax            
            y = self.cells[i, 1] + deltay
            if x < 0 or x > self.max_x or y < 0 or y > self.max_y:
                flag = False
                break 
            if map[y, x] == 1:
                flag = False
                break  
        if flag == True:          
            for i in range(4):
                self.cells[i, 0] += deltax            
                self.cells[i, 1] += deltay
            

class Window(QMainWindow):

    def __init__(self):

        super().__init__()
        self.title = "Tetris Game"
        self.setStyleSheet("background-color: skyblue;")
        self.top= 150
        self.left= 150
        self.width = 1200
        self.height = 1000
        self.starting_x = 5
        self.starting_y = 5
        self.InitWindow()
        self.objectLocationX = 40
        self.objectLocationY = 40
        self.n_x, self.n_y = self.initGrid()
        self.Map = np.zeros((self.n_y, self.n_x))
        type = self.randomType(0,6)
        self.Object = TObject(type, self.n_x - 1, self.n_y - 1)
        self.fillObject(self.Object)
        self.pause = False
        self.createSpeedDiag()      
        self.startTimer(self.speed)
    def UiComponents(self):
        self.text = "null"
        self.score = 0
        self.label = QLabel(self)
        self.label.setGeometry(850, 150, 260, 60)
        self.label.setStyleSheet("QLabel"
        "{"
        "border: 3px solid black;"
        "background: white;"
        "}")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Times', 15))

    def createSpeedDiag(self):
        dlg  = SpeedDialog()
        dlg.exec()
        self.speed = dlg.valueChange()

    def timerEvent(self, event):
        if self.pause == False:
            self.unfillObject(self.Object)
            self.Object.move(0, 1, self.Map)
            self.fillObject(self.Object)
            self.restart()
            self.repaint()

    def keyReleaseEvent(self, event):
        if event.key() == KEY_LEFT:
            self.unfillObject(self.Object)
            self.Object.move(-1, 0, self.Map)
            self.fillObject(self.Object)  
            self.repaint()
        elif event.key() == KEY_RIGHT:
            self.unfillObject(self.Object)
            self.Object.move(1, 0, self.Map)
            self.fillObject(self.Object) 
            self.repaint()
        elif event.key() == KEY_ROTATE:
            self.unfillObject(self.Object)
            self.Object.rotate(self.Map)
            self.fillObject(self.Object)
            self.repaint()
        elif event.key() == KEY_DOWN:
            self.unfillObject(self.Object)
            self.Object.move(0, 1, self.Map)
            self.fillObject(self.Object)
            self.restart()
            self.repaint()
        elif event.key() == KEY_P:
            self.pause = ~self.pause
        elif event.key() == KEY_S:
            self.pause = True
            self.createSpeedDiag()
            self.pause = False

        
        print(event.key()) 
        return super().keyReleaseEvent(event)

                

    def paintEvent(self, event):
        '''
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))
        painter.drawRect(self.objectLocationX, self.objectLocationY, 400, 200)
        ''' 
       
        self.drawGrid()
        self.fillGridCells()
        #self.animation()

    def eraseRow(self):
        nErasedRow = 0
        for row in range(self.n_y):
            sum = 0
            for cell in range(self.n_x):
                sum += self.Map[row, cell]
            if sum == self.n_x:
                self.movecellsdown(row)
                pygame.mixer.init()
                pygame.mixer.music.load("c:\\Coding\\bell.mp3")
                pygame.mixer.music.play()
                nErasedRow += 1 
        if nErasedRow == 1:
            self.score += 1
        elif nErasedRow == 2:
            self.score += 3
        elif nErasedRow == 3:
            self.score += 5
        elif nErasedRow == 4:
            self.score += 8
        self.text = str(self.score)
        print(self.text)
        self.label.setText("Score: " + self.text)

    
    def movecellsdown(self, start_row):
        for row in range(start_row, 0, -1):
            print('test movecelldown: ', row)
            self.Map[row, :] = self.Map[row - 1, :]
        self.Map[0, :] = 0


    def restart(self):
        flag = False
        self.unfillObject(self.Object)
        for ic in range(4):
            x = self.Object.cells[ic, 0]
            y = self.Object.cells[ic, 1] + 1 
            if  y > self.n_y - 1:
                flag = True
                break
            elif self.Map[y, x] == 1:
                flag = True
                break
        self.fillObject(self.Object)
        endGame = self.end_game()

        if flag == True:
            self.eraseRow()
            if endGame == False:
                type = self.randomType(0,6)
                self.Object.re_init(type)
                self.fillObject(self.Object)
            else:
                self.close()


    def end_game(self):
        endGame = False
        for ic in range(self.n_x -1):

            if self.Map[0, ic] == 1:
                endGame = True
                break
        return endGame
        
    
    def randomType(self, start, end):
        typeNumber = random.randint(start,end)
        return typeNumber
          
    def InitWindow(self):

        self.setWindowTitle(self.title)

        self.setGeometry(self.top, self.left, self.width, self.height)

        self.UiComponents()

        self.show()

    def initGrid(self):
        n_x = int((self.width-400)/GridSize)
        n_y = int((self.height-200)/GridSize)
        return n_x, n_y

    def fillObject(self, obj):
        for i in range(4):
            self.Map[obj.cells[i, 1], obj.cells[i, 0]] = 1

    def unfillObject(self, obj):
        for i in range(4):
            self.Map[obj.cells[i, 1], obj.cells[i, 0]] = 0

     

    def fillGridCells(self):
        for ix in range(self.n_x):
            for iy in range(self.n_y):
                if self.Map[iy, ix] == 1:
                    self.fillCell(ix, iy)
                     
#Testing fillcell
    def fillCell(self, x, y):
        coodx = x*GridSize + 5
        coody = y*GridSize + 5
        painter = QPainter(self)
        painter.setBrush(QBrush(Qt.darkBlue, Qt.SolidPattern))
        painter.drawRect(coodx, coody, GridSize, GridSize)

    def drawGrid(self):
        painter = QPainter(self)
        divisions = int((self.width-400)/GridSize)
        painter.setPen(QtCore.Qt.darkCyan)
        x = self.starting_x
        y=  self.starting_y
        for i in range(divisions + 1):
            painter.drawLine(x, self.starting_y, x, self.starting_y + divisions * GridSize)
            x += GridSize
        divisions = int((self.height-200)/GridSize)
        for i in range(divisions + 1):
            painter.drawLine(self.starting_x, y, self.starting_x + divisions * GridSize, y)
            y += GridSize






App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())
