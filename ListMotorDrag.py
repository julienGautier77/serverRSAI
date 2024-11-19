#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# last modified 18 oct 2024


from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QWidget,QMainWindow
from PyQt6.QtWidgets import QVBoxLayout,QHBoxLayout,QPushButton
from PyQt6.QtWidgets import QComboBox,QLabel,QMenuBar
from PyQt6.QtGui import QIcon,QAction
import qdarkstyle
import sys

import time
import ast
import socket as _socket
from PyQt6.QtCore import Qt
from PyQt6 import QtCore
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea import DockArea
import pathlib
import os
from oneMotorGuiServerRSAI import ONEMOTORGUI

class MAINMOTOR(QMainWindow):
    """  widget
    """

    def __init__(self, parent=None):
        
        super(MAINMOTOR, self).__init__(parent)
        p = pathlib.Path(__file__)
        self.isWinOpen = False
        self.parent = parent
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setWindowIcon(QIcon('./icons/LOA.png'))
        self.setWindowTitle('Main Motors')
        p = pathlib.Path(__file__).parent
        sepa = os.sep
        fileconf = str(p) + sepa + "confServer.ini"
        self.confServer = QtCore.QSettings(fileconf,QtCore.QSettings.Format.IniFormat)
        
        server_host = str( self.confServer.value('MAIN'+'/server_host') )# 
        serverPort =int(self.confServer.value('MAIN'+'/serverPort')) # 
        self.clientSocket =_socket.socket(_socket.AF_INET,_socket.SOCK_STREAM)

        try :
            self.clientSocket.connect((server_host,serverPort))
            isconnected = True
        except :
            isconnected = False
        cmdsend = " %s" %('listRack',)
        self.clientSocket.sendall((cmdsend).encode())
        self.listRack = self.clientSocket.recv(1024).decode()
        self.listRack = ast.literal_eval(self.listRack)
        self.IPadress = self.listRack[0]
        self.rackName = []
        self.motorCreatedId = []
        self.motorCreated = []
        self.dictMotor=dict()

        for IP in self.listRack:
            cmd = 'nomRack'
            cmdsend = " %s, %s, %s " %(IP,1,cmd)
            self.clientSocket.sendall((cmdsend).encode())
            nameRack = self.clientSocket.recv(1024).decode().split()[0]
            self.rackName.append(nameRack)
        
        
        rack = dict(zip(self.rackName,self.listRack)) # dictionnaire key name of the rack values IPadress
        self.listMotor = []
        for i in range(0,14):
            cmd = 'name'
            IP = self.listRack[0]
            cmdsend = " %s, %s, %s " %(IP,i+1,cmd)
            self.clientSocket.sendall((cmdsend).encode())
            name = self.clientSocket.recv(1024).decode() #.split()[0]
            self.listMotor.append(name)
        #   self.listMotor =moteurRSAIFDB.listMotorName(self.IPadress) # liste des nom des moteur i+1= numero de l'axe
        self.SETUP()
        self.actionButton()
        
    def SETUP(self):
        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(False)
        self.fileMenu = menuBar.addMenu('&file')
        self.saveAct = QAction('Save',self)
        self.saveAct.triggered.connect(self.saveButton)
        self.fileMenu.addAction(self.saveAct)
        self.vbox = QVBoxLayout()
        hboxRack = QHBoxLayout()
        LabelRack = QLabel('RACK NAME')
        hboxRack.addWidget(LabelRack)
        self.rackChoise = QComboBox()
        hboxRack.addWidget(self.rackChoise)
        i=0
        for rack in self.listRack: #
            InameRack = self.rackName[i]
            self.rackChoise.addItem( InameRack+ '(' + rack +')')
            i+=1

        self.vbox.addLayout(hboxRack)
        LabelMotor = QLabel('Motor NAME')
        hboxRack.addWidget(LabelMotor)
        self.motorChoise = QComboBox()
        hboxRack.addWidget(self.motorChoise)
        self.motorChoise.addItem('Choose a motor')
        self.motorChoise.addItems(self.listMotor)
        self.addButt = QPushButton('add motor')
        hboxRack.addWidget(self.addButt)
        self.displayWidget = QWidget()
        # self.layoutDisplay = QHBoxLayout()
        # self.layoutDisplay.addWidget(self.displayWidget)
        self.vbox.addWidget(self.displayWidget)


        centralWidget = QWidget()
        centralWidget.setLayout(self.vbox)
        self.setCentralWidget(centralWidget)

    def actionButton(self):
        #self.motorChoise.currentIndexChanged.connect(self.createMotor)
        self.rackChoise.currentIndexChanged.connect(self.ChangeIPRack)
        self.addButt.clicked.connect(self.createButton)
    
    def createButton(self):
        if (self.motorChoise.currentIndex() )> 0 :
            self.numMotor = self.motorChoise.currentIndex() # car indice 0 = 'choose o motor'
            self.IPadress = self.listRack [self.rackChoise.currentIndex()]
            motorID = str(self.IPadress) + 'M' + str(self.numMotor)
            if motorID in self.motorCreatedId: 
                print('moteur and button already created')
                index = self.motorCreatedId.index(motorID)
                #self.open_widget(self.motorCreated[index])
            else :
                self.motorWidget = ONEMOTORGUI(self.IPadress,self.numMotor)
                time.sleep(0.1)
                # self.open_widget(self.motorWidget)
                self.motorCreatedId.append(motorID)
                self.motorCreated.append(self.motorWidget)
                self.dictMotor = dict()
                but = DraggableButton(self.motorWidget.name[0],self.displayWidget)
                but.setObjectName(str(motorID))
                but.resize(100,50)
                but.move(20,20)
                but.show()
                but.clicked.connect(lambda:self.open_widget(self.motorWidget))
                
               

    def ChangeIPRack(self):
        self.motorChoise.clear()
        self.IPadress = str( self.listRack[self.rackChoise.currentIndex()])
        #print('ip',self.IPadress)
        self.listMotor = []
        for i in range(0,14):
            cmd = 'name'
            IP = self.IPadress
            cmdsend = " %s, %s, %s " %(IP,i+1,cmd)
            self.clientSocket.sendall((cmdsend).encode())
            name = self.clientSocket.recv(1024).decode() #.split()[0]
            self.listMotor.append(name)

        self.motorChoise.addItem('Choose a motor')
        self.motorChoise.addItems(self.listMotor)
        
    def saveButton(self):
        print('save)')
    def open_widget(self,fene):
        
        """ open new widget 
        """
        if fene.isWinOpen is False:
            #New widget"
            fene.show()
            fene.startThread2()
            fene.isWinOpen = True
        else:
            #fene.activateWindow()
            fene.raise_()
            fene.showNormal()

    def closeEvent(self, event):
        """ 
        When closing the window
        """
        self.fini()
        time.sleep(0.1)
        event.accept()
        
    def fini(self): 
        '''
        at the end we close all the thread 
        '''
        
        self.isWinOpen = False
        for mot in self.motorCreated:
            mot.close()
        time.sleep(0.1)    
        self.clientSocket.close()


class DraggableButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)
        self._drag_active = False
        self.moved  = False

    def mousePressEvent(self, event):
        self.moved  = False
        if event.button() == Qt.MouseButton.RightButton:
            self._drag_active = True
            # Sauvegarder la position de départ de la souris
            self._drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.MouseButton.RightButton:
            if (event.globalPosition().toPoint() - self._drag_start_position).manhattanLength()>10:
                self.moved = True
            # Mettre à jour la position du bouton pendant le glissement
                self.move(event.globalPosition().toPoint() - self._drag_start_position)
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self._drag_active = False
        if self.moved == False:
            self.clicked.emit()
        event.accept()



if __name__ == '__main__':
    appli = QApplication(sys.argv)
    s = MAINMOTOR()
    s.show()
    appli.exec_()