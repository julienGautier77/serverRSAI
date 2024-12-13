#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Server for RSAI racks
synchronisation with RSAI DB (firebird )
control the RSAI rack with PilmotTango.dll & openModbus.dll 

'''

try:
    import moteurRSAIFDB 
except :
    print('connection to firebird problem')
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import qdarkstyle
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QCheckBox
from PyQt6 import QtCore
import pathlib
import os
import time
import sys
import socket as _socket
import uuid
import ctypes
import traceback
import __init__

author = __init__.__author__
version = __init__.__version__


class SERVERRSAI(QWidget):
    signalServer = QtCore.pyqtSignal(object)
    def __init__(self, parent=None):
        
        super(SERVERRSAI, self).__init__(parent)

        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.hostname =_socket.gethostname()
        self.iphost = _socket.gethostbyname(self.hostname)
        
        
        err = self.initFromRSAIDB()    
        self.setup()
        self.connexionRack()

        self.server = SERVER(PilMot=self.PilMot,conf=self.conf,listRackIP=self.listRackIP,dict_moteurs=self.dict_moteurs,parent=self)
        self.server.start() # Demarage du serveur
    
    def initFromRSAIDB(self):

        self.listRackIP = moteurRSAIFDB.rEquipmentList() # list des ip 
        self.rackName = []
        for IP in self.listRackIP:
            self.rackName.append(moteurRSAIFDB.nameEquipment(IP))
        
        self.dictRack = dict(zip(self.rackName,self.listRackIP)) # dictionnaire name  IPadress
        self.dict_moteurs = {} # dictionnaire des dictionnaires de racks et des nom des moteurs

        # creation fichier ini
        self.conf = QtCore.QSettings('confMoteurRSAIServer.ini', QtCore.QSettings.Format.IniFormat)
        i=0
        for ip in self.listRackIP :
            self.listMotorServ = [] # nom qui sert pour le fichier conf.ini
            self.listMotor = moteurRSAIFDB.listMotorName(ip)
            
             # liste des nom des moteur i+1= numero de l'axe correspondant a IP 
            num = list(range(1,len(self.listMotor)+1))
            dict_name = "self.dictMotor"+"_"+str(ip) 
            self.listMotor = [element.replace('Â','') for element in self.listMotor]
            self.listMotor = [element.replace('°','') for element in self.listMotor]
            #self.listMotor = [element.replace(' ','M') for element in self.listMotor]
            
            ii = 0 
            for mot in self.listMotor:
                motConf = moteurRSAIFDB.nameEquipment(ip)+'M'+str(ii+1)
                self.listMotorServ.append(motConf)
                
                if mot == ' ':
                    mot = 'M' +str(ii+1)
                    self.listMotor[ii] = mot 
                ii+= 1
            iii = 0
            # for mot in self.listMotor:
            #     if mot == 'M':
            #         mot = 'M' +str(iii+1)
            #         self.listMotor[iii] = mot 
            #     iii+= 1
            
            self.dict_moteurs[dict_name] = dict(zip(num,self.listMotorServ))
            self.dict_moteurs[dict_name]['ip'] = str(ip)
            
            j = 0
            for mot in self.listMotorServ:
                moteur = moteurRSAIFDB.MOTORRSAI(IpAdrress=ip,NoMotor=j+1)
                name = mot
                nameGiven = self.listMotor[j]
                nomRack = moteur.getEquipementName()  
                step = moteur.step
                butmoins = moteur.butMoins
                butplus = moteur.butPlus
                refName = moteur.refName
                refValue = moteur.refValue
                self.conf.setValue(name+"/nom",nameGiven)
                self.conf.setValue(name+"/nomRack",nomRack)
                self.conf.setValue(name+"/IPRack",ip)
                self.conf.setValue(name+"/numESim",i)
                self.conf.setValue(name+"/numMoteur",j+1)
                self.conf.setValue(name+"/stepmotor",1/float(step))
                self.conf.setValue(name+"/buteePos",butplus)
                self.conf.setValue(name+"/buteeneg",butmoins)
                self.conf.setValue(name+"/moteurType","RSAI")
                for v in range(0,6):
                    if refName[v] == ' ':
                        refName[v] = 'REF'+str(v)
                    self.conf.setValue(name+"/ref"+str(v)+"Name",refName[v])
                    self.conf.setValue(name+"/ref"+str(v)+"Pos",refValue[v])
                j+= 1
            
            i+= 1

    def updateFromRSAI(self):
        print('update from RSAI DB')
        self.initFromRSAIDB()
        return ('OK')
    
    def setup(self):

        self.setWindowIcon(QIcon('./icons/LOA.png'))
        self.setWindowTitle('RSAI SERVER')
        vbox1 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        label = QLabel('Server RSAI  ')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hbox1.addWidget(label)
        vbox1.addLayout(hbox1)
        
        labelIP = QLabel()
        labelIP.setText('IP:'+self.iphost)
        labelPort = QLabel('Port: 5100')
        hbox1.addWidget(labelIP)
        hbox1.addWidget(labelPort)
        hbox0 = QVBoxLayout()
        vbox1.addLayout(hbox0)
        ll = QLabel('Rack connected')
        hbox0.addWidget(ll)
        self.box = []
        i=0
        for name in self.rackName: # create QCheckbox for each rack
            self.box.append(checkBox(name=str(name), ip=self.listRackIP[i], parent=self))
            hbox0.addWidget(self.box[i])
            i+=1

        hbox2 = QHBoxLayout()
        labelClient = QLabel('Clients connected')
        self.clientLabel=QLabel()
        hbox2.addWidget(labelClient)
        hbox2.addWidget(self.clientLabel)
        vbox1.addLayout(hbox2)
        self.setLayout(vbox1)

    def connexionRack(self):
        p = pathlib.Path(__file__)
        sepa = os.sep
        iplist = '' 
        for ip in self.listRackIP:
            iplist = iplist + ip + '       '
        sizeBuffer = len(self.listRackIP)*16
        
        #iplist = '10.0.6.30       10.0.6.31       '
        IPs_C = ctypes.create_string_buffer(iplist.encode(),sizeBuffer )
        
        # open dll
        dll_file = str(p.parent) + sepa +'PilMotTango.dll'
        self.PilMot = ctypes.windll.LoadLibrary(dll_file)
        nbeqp = len(self.listRackIP)
        argout = self.PilMot.Start(ctypes.c_int(nbeqp), IPs_C) # nb equipement , liste IP
        if argout == 1 :
            print('RSAI connection : OK RSAI connected @\n', self.listRackIP)
        else:
            print('RSAI connexion failed')
        # start thread to check if rack is still connected
        self.threadRack = THREADRACKCONNECT(PilMot=self.PilMot, parent=self )
        self.threadRack.start()

    def closeEvent(self, event):
        """ when closing the window
        """
        self.server.stopThread()
        time.sleep(0.2)
        self.threadRack.stopThread()
        time.sleep(1.2)
        try :
            moteurRSAIFDB.closeConnection()
        except : pass
        self.PilMot.Stop()
        time.sleep(0.2)
        event.accept()
       
class SERVER(QtCore.QThread):
    '''Server class with multi clients

    '''

    def __init__(self,PilMot,conf,listRackIP,dict_moteurs,parent=None):
        
        super(SERVER, self).__init__(parent)
        self.parent = parent
        self.serverHost = _socket.gethostname()
        self.serverPort = 5100
        self.PilMot = PilMot
        self.conf = conf
         
        self.listRackIP = listRackIP
        self.dict_moteurs = dict_moteurs
        self.serversocket = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)      # create socket server 
        # self.serversocket.settimeout(5)
        try :
            self.serversocket.bind((self.serverHost,self.serverPort))
            self.isConnected = True
            print('server ready')
        except :
            print('error connection server')
            self.isConnected = True
        self.listClient = []
        self.clientsConnectedSocket = []
        self.clients_ids = []
        self.clientList = dict()
    
    def run(self):#run
        try: 
            while self.isConnected is True :

                print('start lisenning')
                if self.isConnected is True : 
                    self.serversocket.listen(10)
                    client_socket, client_adress = self.serversocket.accept()
                    client_thread = CLIENTTHREAD(client_socket,client_adress,PilMot=self.PilMot,conf=self.conf,listRackIP=self.listRackIP,dict_moteurs=self.dict_moteurs)
                    client_thread.start()
                    client_thread.signalClientThread.connect(self.signalFromClient)
                    client_thread.signalUpdate.connect(self.updateFromRSAI)
                    self.listClient.append(client_thread)

        except :
            #print('error connection')
           self.stopThread()

    def signalFromClient(self,sig):
        client_id = sig[0]
        client_adresse = sig[1]
        if client_adresse == 0:
            #print('del',client_id)
            del self.clientList[client_id]
            
        else:
            self.clientList[client_id] = client_adresse 
        print('new client: ', self.clientList)
        txt= "\n".join([f"{key}: {value}" for key,value in self.clientList.items()])
        self.parent.clientLabel.setText(txt)

    def updateFromRSAI(self,a):
        print('updateFromRSAI dans la class SERVERRSAI')
        self.parent.updateFromRSAI() 
        time.sleep(0.5)
        self.conf = self.parent.conf
        self.listRackIP = self.parent.listRackIP
        self.dict_moteurs =self.parent.dict_moteurs

        for client in self.listClient:
            client.conf = self.conf 
            client.listRackIP = self.listRackIP
            client.dict_moteurs = self.dict_moteurs
            
    def stopThread(self):
        self.isConnected = False
        #print('clossing server')
        time.sleep(0.1)
        for client in self.listClient:
            client.stopThread()
        self.isConnected = False
        time.sleep(1)
        self.serversocket.close()                            
        print('stop server')
        time.sleep(0.1)
        #self.terminate() 

class CLIENTTHREAD(QtCore.QThread):
    '''client class 
    '''
    signalClientThread = QtCore.pyqtSignal(object)
    signalUpdate = QtCore.pyqtSignal(object)

    def __init__(self,client_socket,client_adresse,PilMot,conf,listRackIP,dict_moteurs,parent=None):
        
        super(CLIENTTHREAD, self).__init__(parent)
        self.client_socket = client_socket
        #self.client_socket.settimeout(3)
        self.client_adresse = client_adresse
        self.parent = parent
        self.conf = conf 
        self.PilMot = PilMot
        self.listRackIP = listRackIP
        self.dict_moteurs = dict_moteurs
        self.client_id = str(uuid.uuid4())
        self.stop = False 
        #self.parent.parent.signalServer.connect(self.updateConf)

    def run(self):
        #print('start thread client')
        self.signalClientThread.emit([self.client_id,self.client_adresse])
        try : 
            while True:
                if self.stop is True:
                    break
                try:
                    data = self.client_socket.recv(1024)
                    msgReceived = data.decode().strip()
                    
                    if not msgReceived:
                        print('connection perdue')
                        self.signalClientThread.emit([self.client_id,0])
                        break
                    else: 
                            try :
                                msgsplit = msgReceived.split(',')
                                msgsplit = [msg.strip() for msg in msgsplit]
                                #print(msgsplit)
                                if len(msgsplit)>1:
                                    ip = msgsplit[0]
                                    axe = int(msgsplit[1])
                                    cmd = msgsplit[2]
                                    numEsim = self.listRackIP.index(ip)
                                    dict_name = "self.dictMotor"+"_"+str(ip)
                                    name = self.dict_moteurs[dict_name][axe]
                                    
                                else:
                                    cmd= msgsplit[0]

                                if len(msgsplit)>3:
                                    valueStr =(msgsplit[3])
                                    para3 = str(valueStr) 
                                    try:
                                        value = ctypes.c_int(int(valueStr))
                                    except:
                                        value = 1
                                else:
                                    value = ctypes.c_int(0)
                                      

                                if len(msgsplit)>4:
                                    para4 = (msgsplit[4])
                                    para4 = str(para4)

                                vit  = ctypes.c_int(int(200))
                                
                                
                                if cmd == 'clientid':
                                    sendmsg = self.client_id+'\n'
                                    self.client_socket.sendall(sendmsg.encode())
                                elif cmd == 'dict' :
                                    sendmsg = self.dict_moteurs
                                    self.client_socket.sendall(sendmsg.encode())
                                elif cmd == 'updateFromRSAI':
                                   # print('serveur update fromRSAI')
                                    sendmsg = 'ok'+'\n'
                                    self.client_socket.sendall(sendmsg.encode())
                                    #time.sleep(0.5)
                                    self.signalUpdate.emit('ok')

                                elif cmd == 'listRack':
                                    sendmsg =str(self.listRackIP) + '\n'
                                    print(sendmsg)
                                    self.client_socket.sendall(sendmsg.encode())    

                                elif cmd == 'move':
                                    regCde = ctypes.c_uint(2)
                                    err = self.PilMot.wCdeMot(numEsim , axe, regCde, value, vit)
                                    sendmsg = 'ok'+'\n'
                                    
                                    self.client_socket.sendall(sendmsg.encode())
                                elif cmd == 'rmove':
                                    print('command received', cmd)
                                    regCde = ctypes.c_uint(4)
                                    err = self.PilMot.wCdeMot(numEsim , axe, regCde, value, vit)
                                    sendmsg = 'ok'+'\n'
                                    self.client_socket.sendall(sendmsg.encode())

                                elif cmd =='stop' :
                                    #print('stop')
                                    regCde = ctypes.c_uint(8) # 8 commande pour arreter le moteur
                                    err = self.PilMot.wCdeMot( numEsim , axe, regCde, 0, 0)
                                    
                                    #
                                    sendmsg = 'ok'+'\n'
                                    self.client_socket.sendall(sendmsg.encode())
                                    # regCde = ctypes.c_uint(9) # 9 commande pour devalider les phases
                                    # err = self.PilMot.wCdeMot( numEsim , axe, regCde, 0, 0)
                                    #print('stoperr',err)
                                    
                                elif cmd =='position' :
                                    pos = self.PilMot.rPositionMot(numEsim , axe ) # lecture position theorique en nb pas
                                    sendmsg = str(pos)+'\n'
                                    self.client_socket.sendall(sendmsg.encode())
                                
                                elif cmd == 'etat' :
                                    a = self.PilMot.rEtatMoteur(numEsim , axe)
                                    # a = hex(a)
                                    etatConnection = self.PilMot.rEtatConnexion( ctypes.c_int16(numEsim) ) 
                                    # print('connextion to equipement',etatConnection)
                                    
                                    if etatConnection == 3:
                                        if (a & 0x0800 )!= 0 : # 
                                            etat = 'Poweroff'
                                        elif (a & 0x0200 )!= 0 : # 
                                            etat = 'Phasedebranche'
                                        elif (a & 0x0400 )!= 0 : # 
                                            etat = 'courtcircuit'
                                        elif (a & 0x0001) != 0:
                                            etat = ('FDC+')
                                        elif (a & 0x0002 )!= 0 :
                                            etat = 'FDC-'
                                        elif (a & 0x0004 )!= 0 :
                                            etat = 'Log+'
                                        elif (a & 0x0008 )!= 0 :
                                            etat = 'Log-'
                                        elif (a & 0x0020 )!= 0 :
                                            etat = 'mvt'
                                        elif (a & 0x0080 )!= 0 : # phase devalidé
                                            etat = 'ok'
                                        elif (a & 0x8000 )!= 0 : # 
                                            etat = 'etatCameOrigin'
                                        else:
                                            etat = '?'
                                        
                                    else:
                                        etat = 'errorConnect'
                            
                                    sendmsg = etat
                                    self.client_socket.sendall(sendmsg.encode())
                                    
                                elif cmd == 'setzero' :
                                    regCde = ctypes.c_int(1024) #  commande pour zero le moteur (2^10)
                                    err = self.PilMot.wCdeMot(numEsim , axe,regCde,ctypes.c_int(0),ctypes.c_int(0))
                                    sendmsg = 'ok'
                                    self.client_socket.sendall(sendmsg.encode())
                                    
                                elif cmd == 'name':
                                    nameGiven = str(self.conf.value(name+'/'+'nom'))
                                    sendmsg = nameGiven
                                    self.client_socket.sendall(sendmsg.encode())

                                elif cmd == 'setName':
                                    sendmsg = 'ok'
                                    try :
                                        moteurRSAIFDB.setNameMoteur(ip,axe,para3)
                                    except:
                                        sendmsg = 'errorFB'
                                    self.client_socket.sendall(sendmsg.encode())
                                
                                elif 'ref' in cmd :
                                    ref = str(self.conf.value(name+'/'+str(cmd)))
                                    sendmsg = ref
                                    self.client_socket.sendall(sendmsg.encode())

                                elif cmd == 'setRefPos':
                                    sendmsg = 'ok'
                                    nRef = int(para4)
                                    valPos = int(para3)
                                    try :
                                        moteurRSAIFDB.setPosRef(ip,axe,nRef,valPos)
                                    except : 
                                        sendmsg = 'errorFB'
                    
                                    self.conf.setValue(name+"/ref"+str(nRef-1)+"Pos",valPos)
                                    self.client_socket.sendall(sendmsg.encode())
                                    
                                elif cmd == 'setRefName':
                                    sendmsg = 'ok'
                                    
                                    nRef = int(para4)
                                    try :
                                        moteurRSAIFDB.setNameRef(ip,axe,nRef,para3)
                                    except:
                                        sendmsg = 'error FB'
                                    self.conf.setValue(name+"/ref"+str(nRef-1)+"Name",para3)
                                    self.client_socket.sendall(sendmsg.encode())

                                elif cmd == 'step': 
                                    
                                    st = str(self.conf.value(name+'/'+'stepmotor'))
                                    
                                    sendmsg = st 
                                    self.client_socket.sendall(sendmsg.encode())
                                    
                                elif cmd == 'buteePos' or 'buteeneg' :
                                    but = str(self.conf.value(name+'/'+cmd))
                                    sendmsg = but 
                                    self.client_socket.sendall(sendmsg.encode())
                                
                                
                                elif cmd == 'nomRack':
                                    
                                    nameRack = str(self.conf.value(name+'/' + cmd))
                                    sendmsg = nameRack
                                    self.client_socket.sendall(sendmsg.encode())
                                else:
                                    sendmsg = 'error '
                                    self.client_socket.sendall(sendmsg.encode())
                            except:
                                print('error')
                                sendmsg = 'error'
                                traceback.print_exc()
                                self.client_socket.sendall(sendmsg.encode())
                                
                except ConnectionResetError:
                    print('deconnection du client')
                    self.client_socket.close()
                    self.signalClientThread.emit([self.client_id,0])
                    break
                                   
        except Exception as e: 
            print('exception server',e)
            self.client_socket.close()
            self.signalClientThread.emit([self.client_id,0])

    def updateConf(self,dat):

        print('update conf client')

        ''' update conf rt.. depuis rsai fb
        '''
        self.conf = dat[0]
        self.listRackIP= [1]
        self.dict_moteurs =[2]
        print('update conf client')

    def stopThread(self):
        self.stop = True     
            
class checkBox(QCheckBox):
    # homemade QCheckBox

    def __init__(self,name='test',ip='', parent=None):
        super(checkBox, self).__init__()
        self.parent = parent 
        self.ip = ip
        self.name = name
        self.setText(self.name+' ( '+ self.ip+ ')')
        self.setObjectName(self.ip)


class THREADRACKCONNECT(QtCore.QThread):
    '''Thread to check if the rack is connected
    '''
    def __init__(self,PilMot,parent=None):
        super(THREADRACKCONNECT,self).__init__(parent)

        self.parent = parent
        self.PilMot = PilMot
        self.stop = False

    def run(self):
        while True:
            
            if self.stop is True:
                break
            else:
                nbEqu=len(self.parent.listRackIP)
                for numEsim in range(0,nbEqu):
                    rcon = self.PilMot.rEtatConnexion( ctypes.c_int16(numEsim) )
                    if rcon == 3:
                        self.parent.box[numEsim].setChecked(True)
                    else: 
                        self.parent.box[numEsim].setChecked(False)
                    time.sleep(1)


    def stopThread(self):
        self.stop = True   
                    
if __name__=='__main__':

    appli = QApplication(sys.argv)
    s = SERVERRSAI()
    s.show()
    appli.exec()