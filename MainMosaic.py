#! /home/upx/loaenv/bin/python3.12
# -*- coding: utf-8 -*-
#last modified 18 oct 2024

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QIcon
import qdarkstyle,sys
import ast
import socket as _socket
import time
from oneMotorGuiServerRSAI import ONEMOTORGUI


class MAINMOTOR(QWidget):
    """  widget
 
    """
    def __init__(self, parent=None):
        print('ini')
        super(MAINMOTOR, self).__init__(parent)

        self.isWinOpen = False
        self.parent = parent
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setWindowIcon(QIcon('./icons/LOA.png'))
        self.setWindowTitle('Main Motors')

        self.server_host = '10.0.6.12'
        self.serverPort = 5100
        self.clientSocket = _socket.socket(_socket.AF_INET,_socket.SOCK_STREAM)

        try :
            self.clientSocket.connect((self.server_host,self.serverPort))
            self.isconnected = True
        except :
            self.isconnected = False
        
        self.aff()

    def aff(self):
        cmdsend = " %s" %('listRack',)
        self.clientSocket.sendall((cmdsend).encode())
        self.listRack = self.clientSocket.recv(1024).decode()
        self.listRack = ast.literal_eval(self.listRack)
        
        self.rackName = []
        self.motorCreatedId = []
        self.motorCreated = []

        for IP in self.listRack:
            cmd = 'nomRack'
            cmdsend = " %s, %s, %s " %(IP,1,cmd)
            self.clientSocket.sendall((cmdsend).encode())
            nameRack = self.clientSocket.recv(1024).decode().split()[0]
            self.rackName.append(nameRack)

        
        rack = dict(zip(self.rackName,self.listRack)) # dictionnaire key name of the rack values IPadress
        self.listMotorName = []
        self.listMotButton =list()
        irack = 0 

        for IP in self.listRack: 
            for i in range(0,14):
                cmd = 'name'
                cmdsend = " %s, %s, %s " %(IP,i+1,cmd)
                self.clientSocket.sendall((cmdsend).encode())
                name = self.clientSocket.recv(1024).decode().split()[0]
                self.listMotorName.append(name)
                self.listMotButton.append(QPushButton(name,self))
            irack+=1
        # print(self.listMotorName,len(self.listMotorName),len(self.listMotButton))
        
        self.SETUP()
        self.actionButton()

    def SETUP(self):
        vbox1 = QVBoxLayout()
        grid = QGridLayout()
        z = 0
        for i in range (0,len(self.listRack)):
            grid.addWidget(QLabel(self.rackName[i]),0,i)
            for j in range (0,14):
                grid.addWidget(self.listMotButton[z],j+1,i)
                self.listMotButton[z].clicked.connect(lambda checked, j=j:self.actionPush(j+1,i))
                z+= 1
        vbox1.addLayout(grid)
        self.upRSAI = QPushButton('Update from RSAI')
        self.upRSAI.setDisabled(True)
        vbox1.addWidget(self.upRSAI)
        self.setLayout(vbox1)
        
    def actionPush(self,j,i):
        i = i-1
        print(i,j)
        numMot = j
        ip = self.listRack[i]
        motorID = str(ip)+'M'+str(numMot)
        if motorID in self.motorCreatedId: 
            index = self.motorCreatedId.index(motorID)
            self.open_widget(self.motorCreated[index])
        else :
            self.motorWidget = ONEMOTORGUI(ip,numMot)
            time.sleep(0.1)
            self.open_widget(self.motorWidget)
            self.motorCreatedId.append(motorID)
            self.motorCreated.append(self.motorWidget)

    def actionButton(self):
        self.upRSAI.clicked.connect(self.updateFromRsai)
         

    def updateFromRsai(self):

        print('update')
        cmdsend = " %s" %('updateFromRSAI',)
        self.clientSocket.sendall((cmdsend).encode())
        errr = self.clientSocket.recv(1024).decode()
        self.listMotorName = []
        self.listMotButton =list()
        irack = 0 

        for IP in self.listRack: 
            for i in range(0,14):
                cmd = 'name'
                cmdsend = " %s, %s, %s " %(IP,i+1,cmd)
                self.clientSocket.sendall((cmdsend).encode())
                name = self.clientSocket.recv(1024).decode().split()[0]
                self.listMotorName.append(name)
                self.listMotButton.append(QPushButton(name,self))
            irack+=1
        
        print(self.listMotorName)

    def open_widget(self,fene):
        
        """ open new widget 
        """
        if fene.isWinOpen is False:
            #New widget"
            fene.show()
            fene.startThread2()
            fene.isWinOpen=True
        else:
            #fene.activateWindow()
            fene.raise_()
            fene.showNormal()

    def closeEvent(self, event):
        """ 
        When closing the window
        """
        self.isWinOpen=False
        for mot in self.motorCreated:
            mot.close()
        time.sleep(0.1)    
        self.clientSocket.close()
        time.sleep(0.1)
        event.accept()
        
    
if __name__ == '__main__':
    appli = QApplication(sys.argv)
    s = MAINMOTOR()
    s.show()
    appli.exec_()