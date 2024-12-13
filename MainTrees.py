#! /home/upx/loaenv/bin/python3.12
# -*- coding: utf-8 -*-
#last modified 18 oct 2024

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QTreeWidget,QTreeWidgetItem
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QIcon
import qdarkstyle,sys
import ast
import socket as _socket
import time
import os
import pathlib
from oneMotorGuiServerRSAI import ONEMOTORGUI
from PyQt6 import QtCore

class MAINMOTOR(QWidget):
    """  widget tree with IP adress and motor
 
    """
    def __init__(self, parent=None):

        super(MAINMOTOR, self).__init__(parent)
        self.isWinOpen = False
        self.parent = parent
        p = pathlib.Path(__file__)
        sepa = os.sep
        self.icon = str(p.parent) + sepa + 'icons' + sepa
        self.isWinOpen = False
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setWindowIcon(QIcon(self.icon + 'LOA.png'))
        self.setWindowTitle('Client RSAI')
        p = pathlib.Path(__file__).parent
        sepa = os.sep
        fileconf = str(p) + sepa + "confServer.ini"
        self.confServer = QtCore.QSettings(fileconf,QtCore.QSettings.Format.IniFormat)
        self.server_host = str( self.confServer.value('MAIN'+'/server_host') )# 
        self.serverPort =int(self.confServer.value('MAIN'+'/serverPort'))
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
        self.motItem = []
        self.rackName = []
        self.motorCreatedId = []
        self.motorCreated = []

        for IP in self.listRack:
            cmd = 'nomRack'
            cmdsend = " %s, %s, %s " %(IP,1,cmd)
            self.clientSocket.sendall((cmdsend).encode())
            nameRack = self.clientSocket.recv(1024).decode().split()[0]
            self.rackName.append(nameRack)

        
        self.rack = dict(zip(self.rackName,self.listRack)) # dictionnaire key name of the rack values IPadress
        self.listMotorName = []
        self.listMotButton = list()
        irack = 0 
        self.dic_moteurs={}

        for IP in self.listRack: 
            dict_name = "self.dictMotor" + "_" + str(IP)
            num = list(range(1,15))
            listMot = []
            for i in range(0,14):
                cmd = 'name'
                cmdsend = " %s, %s, %s " %(IP,i+1,cmd)
                self.clientSocket.sendall((cmdsend).encode())
                name = self.clientSocket.recv(1024).decode().split()[0]
                self.listMotorName.append(name)
                listMot.append(name)
                #self.listMotButton.append(QPushButton(name,self))
            irack+=1
        # print(self.listMotorName,len(self.listMotorName),len(self.listMotButton))
            self.dic_moteurs[dict_name] = dict(zip(listMot,num))
            self.dic_moteurs[dict_name]['ip'] = str(IP)
        
        self.SETUP()
        #self.actionButton()

    def SETUP(self):
        vbox1 = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.header().hide()
        z = 0
        for i in range (0,len(self.listRack)):
            rackTree = QTreeWidgetItem(self.tree,[self.rackName[i]])
            for j in range (0,14):
                self.motItem.append( QTreeWidgetItem(rackTree,[self.listMotorName[z],'']))
                z+= 1
        vbox1.addWidget(self.tree)
        self.setLayout(vbox1)
        self.tree.itemClicked.connect(self.actionPush)

    def actionPush(self,item:QTreeWidgetItem,colum:int):
        if item.parent() :
            rackname = item.parent().text(0)
            motorname = item.text(0)
            ip = self.rack[rackname]
            numMot = self.dic_moteurs["self.dictMotor" + "_" + str(ip)][item.text(0)]
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
        self.listMotButton = list()
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
        self.isWinOpen = False
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