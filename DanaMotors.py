#!/home/sallejaune/loaenv/bin/env python
# -*- coding: utf-8 -*-
#last modified 18 oct 2024

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QTreeWidget,QTreeWidgetItem
from PyQt6.QtWidgets import QLabel,QSizePolicy,QTreeWidgetItemIterator
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import qdarkstyle,sys
import ast
import socket as _socket
import time
import os
import pathlib
from oneMotorGuiServerRSAI import ONEMOTORGUI
from threeMotorGuiFB import THREEMOTORGUI
from TiltGui import TILTMOTORGUI
from PyQt6 import QtCore
import tirSalleJaune as tirSJ


class MAINMOTOR(QWidget):
    """  widget tree with IP adress and motor
 
    """
    def __init__(self, chamber=None,parent=None):

        super(MAINMOTOR, self).__init__(parent)
        self.isWinOpen = False
        self.parent = parent
        p = pathlib.Path(__file__)
        sepa = os.sep
        self.icon = str(p.parent) + sepa + 'icons' + sepa
        self.isWinOpen = False
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setWindowIcon(QIcon(self.icon + 'LOA.png'))
        
        p = pathlib.Path(__file__).parent
        sepa = os.sep
        fileconf = str(p) + sepa + "confServer.ini"
        self.confServer = QtCore.QSettings(fileconf,QtCore.QSettings.Format.IniFormat)
        self.server_host = str( self.confServer.value('MAIN'+'/server_host') )# 
        self.serverPort =int(self.confServer.value('MAIN'+'/serverPort'))
        self.clientSocket = _socket.socket(_socket.AF_INET,_socket.SOCK_STREAM)
        self.chamber = chamber
        try :
            self.clientSocket.connect((self.server_host,self.serverPort))
            self.isconnected = True
        except :
            self.isconnected = False
        self.widdgetTir = tirSJ.SalleJauneConnect()
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
                
            irack+=1
            self.dic_moteurs[dict_name] = dict(zip(listMot,num))
            self.dic_moteurs[dict_name]['ip'] = str(IP)
       
        self.rackNameFilter = []
        self.listMotorNameFilter = []
        if self.chamber is not None:
            for name in self.rackName:
                if self.chamber in name.lower():
                    self.rackNameFilter.append(name)
            self.rackIPFilter = []
            for key in self.rack.keys():
                if self.chamber in key.lower():
                    self.rackIPFilter.append(self.rack[key])
            for IP in self.rackIPFilter: 
                for i in range(0,14):
                    cmd = 'name'
                    cmdsend = " %s, %s, %s " %(IP,i+1,cmd)
                    self.clientSocket.sendall((cmdsend).encode())
                    name = self.clientSocket.recv(1024).decode().split()[0]
                    self.listMotorNameFilter.append(name)
                    
        self.SETUP()
        self.EXPAND()

    def SETUP(self):
        vbox1 = QVBoxLayout()

        vbox1.addWidget(self.widdgetTir)
        chamberName = QLabel()
        chamberName.setText('Motors Control: %s' % self.chamber)
        chamberName.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox1.addWidget(chamberName)
        self.tree = QTreeWidget()
        self.tree.header().hide()
        z = 0
        if self.chamber is not None:
            self.setWindowTitle('  Client RSAI  ' + self.chamber)
            for i in range (0,len(self.rackNameFilter)):
                rackTree = QTreeWidgetItem(self.tree,[self.rackNameFilter[i]])
                for j in range (0,14):
                    self.motItem.append( QTreeWidgetItem(rackTree,[self.listMotorNameFilter[z],'']))
                    z+= 1  
        else :
            self.setWindowTitle('Client RSAI ')
            for i in range (0,len(self.listRack)):
                rackTree = QTreeWidgetItem(self.tree,[self.rackName[i]])
                for j in range (0,14):
                    self.motItem.append( QTreeWidgetItem(rackTree,[self.listMotorName[z],'']))
                    z+= 1

        vbox1.addWidget(self.tree)
        self.setLayout(vbox1)

        self.tree.itemClicked.connect(self.actionPush)
        self.tree.itemExpanded.connect(self.EXPAND)
        self.tree.itemCollapsed.connect(self.EXPAND)
        self.resize(self.sizeHint().width(),self.minimumHeight())
        self.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum)
        
        ################################################################################################""
        # Special Button

        grid_layout = QGridLayout()
        self.cible = THREEMOTORGUI(IPVert='10.0.6.30', NoMotorVert = 7 , IPLat='10.0.6.30', NoMotorLat = 13,IPFoc='10.0.6.30', NoMotorFoc= 12,nomWin='DANA JET',nomTilt='JET1',nomFoc='Jet Foc')
        self.cible_But = QPushButton('JET')
        self.cible_But.clicked.connect(lambda:self.open_widget(self.cible))

        self.camWidget = THREEMOTORGUI(IPVert='10.0.6.30', NoMotorVert = 2 , IPLat='10.0.6.31', NoMotorLat = 11,IPFoc='10.0.6.31', NoMotorFoc= 12,nomWin='Focal Spot DANA',nomTilt='CAM FS',nomFoc='')
        self.cam_But = QPushButton('CAM')
        self.cam_But.clicked.connect(lambda:self.open_widget(self.camWidget))

        self.P1TB = TILTMOTORGUI('10.0.6.31',1,'10.0.6.31',2,nomWin='P1 Turning Box ',nomTilt='P1 TB')
        self.P1TB_But = QPushButton('P1 TB')
        self.P1TB_But.clicked.connect(lambda:self.open_widget(self.P1TB))

        # self.P2TB = TILTMOTORGUI('10.0.1.30',3,'10.0.1.30',4,nomWin='P2 Turning Box ',nomTilt='P2TB')
        self.P2TB_But = QPushButton('P2 TB')
        self.P2TB_But.setEnabled(False)
        # self.P2TB_But.clicked.connect(lambda:self.open_widget(self.P2TB))

        self.P3TB = TILTMOTORGUI('10.0.6.31',3,'10.0.6.31',4,nomWin='P3 Turning Box ',nomTilt='P3TB')
        self.P3TB_But = QPushButton('P3 TB')
        self.P3TB_But.clicked.connect(lambda:self.open_widget(self.P3TB))

        self.P1M = TILTMOTORGUI('10.0.6.31',5,'10.0.1.31',6,nomWin='P1 mirror  ',nomTilt='P1 M')
        self.P1Mir_But = QPushButton('P1 Mir')
        self.P1Mir_But.clicked.connect(lambda:self.open_widget(self.P1M))
        
        self.P2Mir_But = QPushButton('P2 Mir')
        self.P2Mir_But.setEnabled(False)
        self.P3M = TILTMOTORGUI('10.0.6.31',7,'10.0.1.31',8,nomWin='P3 mirror  ',nomTilt='P1 M')
        self.P3Mir_But = QPushButton('P3 Mir')
        self.P1Mir_But.clicked.connect(lambda:self.open_widget(self.P3M))

        self.P1OPA = TILTMOTORGUI('10.0.1.31',9,'10.0.1.31',10,nomWin='P1 Spherique  ',nomTilt='P1 Sphe')
        self.P1OAP_But = QPushButton('P1 OAP')
        self.P1OAP_But.clicked.connect(lambda:self.open_widget(self.P1OPA ))
        
        grid_layout.addWidget(self.P1TB_But,0,0)
        grid_layout.addWidget(self.P2TB_But,0,1)
        grid_layout.addWidget(self.P3TB_But,0,2)
        grid_layout.addWidget(self.P1Mir_But,1,0)
        grid_layout.addWidget(self.P2Mir_But,1,1)
        grid_layout.addWidget(self.P3Mir_But,1,2)
        grid_layout.addWidget(self.P1OAP_But ,2,0)
        grid_layout.addWidget(self.cible_But,2,1)
        grid_layout.addWidget(self.cam_But ,2,2)
        
        vbox1.addLayout(grid_layout)
        

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

    def EXPAND(self):
        row = 20
        rowH = self.tree.sizeHintForRow(0)
        totalH = row * rowH 
        count = 0
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            if item.parent():
                if item.parent().isExpanded():
                    count +=1
            else:
                count += 1
            iterator += 1

        totalH = row * count 
        self.resize(self.sizeHint().width(),totalH + 50)

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
    
    s = MAINMOTOR(chamber ='dana')
    s.show()
    appli.exec_()