# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 18:01:56 2022

@author: GAUTIER
"""
from firebird.driver import connect    ### pip install  firebird-driver
import time
from pyqtgraph.Qt import QtCore

# if not local  dsn=10.0.5.X/ ??

## connection to data base 
con = connect('C:\PilMotDB\PILMOTCONFIG.FDB', user='sysdba', password='masterkey')
cur = con.cursor()

listParaStr ={'nomAxe' : 2 ,'nomEquip':10, 'nomRef1': 1201 , 'nomRef2':1202 , 'nomRef3':1203 , 'nomRef4':1204 , 'nomRef5':1205 , 'nomRef6':1206 , 'nomRef7':1207 , 'nomRef8':1208 , 'nomRef9':1209 , 'nomRef10':1210}
listParaReal = {'Step':1106 , 'Ref1Val': 1211 , 'Ref2Val':1212 , 'Ref3Val':1213 , 'Ref4Val':1214 , 'Ref5Val':1215 , 'Ref6Val':1216 , 'Ref7Val':1217 , 'Ref8Val':1218 , 'Ref9Val':1219 , 'Ref10Val':1220}
listParaInt = {'ButLogPlus': 1009 , 'ButLogNeg':1010 }


def listProgConnected():
    # Read the list of programs connected to database
    # nbProgConnected :  number of programs connected into database
    # p_ListPrg (returned): Described list of programs into database
    #  (Format of the field of the list for one program: PkId, UUID, SoftName, Alias, Hostname, IpAddress, TimeConnection, HeartCnt)
    
    SoftName = []
    HostName = []
    IpProgram = []

    cur.execute("SELECT * FROM " + "TBCONNECTEDLIST" + " ORDER BY PkId;" )

    for row in cur:
        SoftName.append(row[2])
        HostName.append(row[4])
        IpProgram.append(row[5])
    nbProgConnected = len(SoftName)

    return nbProgConnected, SoftName, HostName, IpProgram

def rEquipmentList():
    # Read the list of Equipment connected to database equipement =Rack =IPadress 
    #Described list of equipment into database
    # Format of the field of the list for one equipment: PkId, Address, Category, Status)

    addressEquipement=[]
    cur.execute("SELECT * FROM " + "TBEQUIPMENT")
    for row in cur:
        addressEquipement.append (row[1])
    return addressEquipement



def rEquipmentIdNbr(IpAddress):
    # Get Identification number of one PilMot equipement from its IP Address
    # IpAddress: IP Address
    #p_IdEquipment: Identification number of the equipement

    p_IdEquipment = getValueWhere1ConditionAND("TbEquipment", "PkId", "Address", IpAddress)
    return p_IdEquipment

def rEquipmentStatus(IpAddress): 
    # Read the status of an equipment from its IP Address

    status =getValueWhere1ConditionAND("TbEquipment", "status", "Address", IpAddress)
    return status

def getSlotNumber(NoMotor):
    # Get the slot number of ESBIM corresponding to the motor number
    # return Slot number (value from 1 to 7)

    SlotNbr = 0
    SlotNbr = (NoMotor + 1 ) / 2
    return SlotNbr

def getAxisNumber(NoMotor):
 #Get the axis number of module corresponding to the motor number
 #return Slot number (value 1 or 2)

    AxisNbr = 1
    if(NoMotor % 2) == 0:
        AxisNbr = 2
    return AxisNbr




def readPkModBim2BOC(PkEsbim, NumSlotMod, NumAxis, FlgReadWrite=1):
    #  Read Primary key identifier of an axis module Bim2BOC :  p_PkModBim
    #  PkEsbim : numero Equipment on which the module is plugged
    #  NumSlotMod : Number of the slot of the module to get PK
    #  NumAxis : Axis number of the module
    #  param FlgReadWrite : Indicate if the function accesses to Read or Write table (value : 1=ReadTb, 0=WriteTb)
  
    TbToRead = "TbBim2Boc_1Axis_W"
    
    cur.execute( "SELECT m.PkId FROM TbModule m INNER JOIN TbEquipment e ON m.idEquipment = e.PKID WHERE (e.PkId = " + str(int(PkEsbim)) + " and m.NumSlot = " + str(int(NumSlotMod)) + ");" )
    
    for row in cur:
       #print(row)
        TmpPkModBim = row[0]   # cle dans TbModule correspondant cle Esbim dans TbEquipement et numero du slot  

    cur.execute( "SELECT b.PkId FROM " + TbToRead + " b WHERE IdModule = " + str(TmpPkModBim) + " AND NumAxis = " + str(NumAxis) + ";" );
    for row in cur :
        p_PKModBim =row[0]
    return p_PKModBim # cle dans TbBim2Boc_1Axis_W correpondant idmodule et au numero d axe


def getValueWhere1ConditionAND(TableName, ValToRead, ConditionColName,ConditionValue):
    # Read the field value in a table where the 'column' equals 'value' corresponding Query = SELECT 'ValToRead'  FROM TableName WHERE ConditionColName = ConditionValue
    # TableName : Table in which execute query
    # ValToRead : Field Value to read
    # ConditionColName : Column name for the condition of the query search
    # ConditionValue : Value name for the condition of the query search
    # return param p_DataRead : values read

    cur.execute( "SELECT " + ValToRead  + " FROM " + TableName + " WHERE " + ConditionColName + " = '" + ConditionValue + "' ;" )
    for row in cur:
        p_DataRead=row[0]
    
    return p_DataRead

def getValueWhere2ConditionAND(TableName, ValToRead, ConditionColName1, ConditionValue1, ConditionColName2, ConditionValue2):
    #  Read the field value in a table where the 'column' equals 'value' corresponding Query = SELECT 'ValToRead' FROM TableName WHERE 'ConditionColName1' = 'ConditionValue1' AND 'ConditionColName2' = 'ConditionValue2' "
    #  TableName : Table in which execute query
    #  ValToRead : Field Value to read
    #  ConditionColName1 : First column name for the condition of the query search
    #  ConditionValue1 : First value name for the condition of the query search
    #  ConditionColName2 : Second column name for the condition of the query search
    #  ConditionValue2 : Second value name for the condition of the query search
    # return p_DataRead : values read

    cur.execute("SELECT " + ValToRead  + " FROM " + TableName + " WHERE " + ConditionColName1 + " = '" + ConditionValue1 + "' AND " + ConditionColName2 + " = '" + ConditionValue2 + "' ;" )
    for row in cur:
        p_DataRead=row[0]
    return p_DataRead

def getValueWhere3ConditionAND(TableName, ValToRead,  ConditionColName1, ConditionValue1, ConditionColName2, ConditionValue2, ConditionColName3,  ConditionValue3):
    #  Read the field value in a table where the 'column' equals 'value' corresponding Query = SELECT 'ValToRead' FROM TableName WHERE 'ConditionColName1' = 'ConditionValue1' AND 'ConditionColName2' = 'ConditionValue2' " ...
    #  param TableName : Table in which execute query
    #  ValToRead : Field Value to read
    #  ConditionColName1 : First column name for the condition of the query search
    #  ConditionValue1 : First value name for the condition of the query search
    #  ConditionColName2 : Second column name for the condition of the query search
    #  ConditionValue2 : Second value name for the condition of the query search
    #  ConditionColName3 : Third column name for the condition of the query search
    #  ConditionValue3 : Third value name for the condition of the query search

    cur.execute( "SELECT " + ValToRead  + " FROM " + TableName + " WHERE " + ConditionColName1 + " = '" + ConditionValue1 + "' AND " + ConditionColName2 + " = '" + ConditionValue2 + "' AND " + ConditionColName3 + " = '" + ConditionValue3 + "' ;" )
    for row in cur:
        p_DataRead=row[0]
    return p_DataRead

def rPositionMot(IdEquipt , NoMotor):
    # Read the position of the Motor with IdEquipt
    NoMod  = getSlotNumber(NoMotor)
    NoAxis = getAxisNumber(NoMotor)

    TbToRead = "TbBim2Boc_1Axis_R"
    PkIdTbBoc = readPkModBim2BOC(IdEquipt, NoMod, NoAxis, FlgReadWrite=1) # Read Primary key identifier of an axis module Bim2BOC :  p_PkModBim
    posi=getValueWhere1ConditionAND("TbBim2BOC_1Axis_R", "PosAxis", "PkId", str(PkIdTbBoc))
    #print('posi',posi)
    return posi

def positionMot(IpAdress,NoMotor):
    # Read the position of the Motor with IpAdress
    IdEquipt = rEquipmentIdNbr(IpAdress)
    posi = rPositionMot(IdEquipt,1)
    return posi

def rStepperParameter(IdEquipt,NoMotor, NoParam):
    #  Read one stepper parameter
    #  param IdEquipt: Ident of equipment to read
    #  NoMotor: number of the motor on the equipment
    # NoParam: number(Id) of the parameter to read

    NoMod  = getSlotNumber(NoMotor)
    NoAxis = getAxisNumber(NoMotor)
    PkIdTbBoc = readPkModBim2BOC(IdEquipt, NoMod, NoAxis, FlgReadWrite=1) # Read Primary key identifier of an axis module Bim2BOC :  p_PkModBim
    #print('PkIdTbBoc',PkIdTbBoc)
    PkIdModuleBIM = getValueWhere2ConditionAND( "TbBim2BOC_1Axis_R", "IdModule", "PkId", str(PkIdTbBoc), "NumAxis", str(NoAxis))
    # dans la table TbBim2BOC_1Axis_R on lit la  valeur de IdModule pourlaquelle PkID=PkIdTbBoc et NumAxis=NoAxis
    #print('PkIdModuleBIM',PkIdModuleBIM)
    #print('number parameter',NoParam)
    
    if NoParam  in listParaStr.values()  : # ou autre str 
        
        tbToread = "TbParameterSTR"
        p_ReadValue = getValueWhere3ConditionAND(tbToread, "ValParam", "IdName", str(NoParam), "IdModule", str(PkIdModuleBIM), "NumAxis", str(NoAxis))
        return p_ReadValue    
    if NoParam in listParaReal.values():
        tbToread="TbParameterREAL"
        p_ReadValue = getValueWhere3ConditionAND(tbToread, "ValParam", "IdName", str(NoParam), "IdModule", str(PkIdModuleBIM), "NumAxis", str(NoAxis))
        return p_ReadValue 
    if  NoParam in listParaInt.values():
        tbToread="TbParameterINT"
        p_ReadValue = getValueWhere3ConditionAND(tbToread, "ValParam", "IdName", str(NoParam), "IdModule", str(PkIdModuleBIM), "NumAxis", str(NoAxis))
        return p_ReadValue 
    else :
        print( 'parameter value not valid')
        return 0


# TABLE_NAME ='TbParameterSTR'
# SELECT = 'select * from %s where IdName=1201 '% TABLE_NAME
# # # #PKID,IDMODULE,IDNAME,VALPARAM,NUMAXI,CATEGORY
# cur.execute(SELECT)
# print(cur.fetchall())

def nameMoteur(IpAdress,NoMotor):
    IdEquipt = rEquipmentIdNbr(IpAdress)
    name=rStepperParameter(IdEquipt,NoMotor,listParaStr['nomAxe'])
    return name
def refName(IpAdress,NoMotor,NRef):
    # name of the absolute reference (statrt 1)
    IdEquipt = rEquipmentIdNbr(IpAdress)
    key=listParaStr['nomRef'+str(NRef)]
    nameRef = rStepperParameter(IdEquipt,NoMotor,key)
    return nameRef

def refValue(IpAdress,NoMotor,NRef):
    # name of the absolute reference (statrt 1)
    IdEquipt = rEquipmentIdNbr(IpAdress)
    key=listParaReal['Ref'+str(NRef)+'Val']
    nameRef = rStepperParameter(IdEquipt,NoMotor,key)
    return nameRef

def stepValue(IpAdress,NoMotor,NRef):
    # Valeur de 1 pas dans l'unites
    IdEquipt = rEquipmentIdNbr(IpAdress)
    key=listParaReal['Step'] #1106
    return rStepperParameter(IdEquipt,NoMotor,key)

def butLogPlusValue(IpAdress,NoMotor):
    IdEquipt = rEquipmentIdNbr(IpAdress)
    key=listParaInt['ButLogPlus'] 
    return rStepperParameter(IdEquipt,NoMotor,key)

def listMotor(IpAdress):
    #  List des moteurs sur l'equipement IpAdress
    IdEquipt = rEquipmentIdNbr(IpAdress)
    PkidModule=[]
    SELECT = 'select PkId from %s  where  IdEquipment= %s and NumSlot>=0'% ('TbModule',str(IdEquipt))   # list Pkid module
    cur.execute(SELECT)
    for row in cur :
       PkidModule.append(row[0])
    # print('liste module de l equipement',PkidModule)
    listPidAxis=[]
    for idModule in PkidModule:
        SELECT = 'select PkId from %s  where  IdModule= %s '% ('TbBim2BOC_1Axis_R',str(idModule))   #list Pkid Axis
        cur.execute(SELECT)
        for row in cur:
            listPidAxis.append(row[0])
    # print(listPidAxis)
    listNameMotor=[]
    for noMot in listPidAxis:
        listNameMotor.append(nameMoteur(IpAdress,noMot))
    return listNameMotor
    
def nameEquipment(IpAdress):
    IdEquipt = rEquipmentIdNbr(IpAdress)
    
    SELECT = 'select PkId from %s  where  IdEquipment = %s and NumSlot = -1'% ('TbModule',str(IdEquipt))   # list Pkid module
    cur.execute(SELECT)
    for row in cur :
        PkIdMod = row[0]
    
    SELECT = 'select ValParam from %s where IDMODULE = %s and IDNAME = 10 '% ('TbParameterSTR',str(PkIdMod))
    cur.execute(SELECT)
    for row in cur :
        nameEquip=row[0]
    return nameEquip

def nameMotorToNum(IpAdress,name):
    return


def rMotorStatus(IpAdress,NoMotor):
    # read status of the motor
    IdEquipt = rEquipmentIdNbr(IpAdress)
    NoMod  = getSlotNumber(NoMotor)
    NoAxis = getAxisNumber(NoMotor)
    
    TbToRead = "TbBim2Boc_1Axis_R"
    PkIdTbBoc = readPkModBim2BOC(IdEquipt, NoMod, NoAxis, FlgReadWrite=1) # Read Primary key identifier of an axis module Bim2BOC :  p_PkModBim
    return(getValueWhere1ConditionAND("TbModule", "StatusAxis", "PkId", str(PkIdTbBoc)))



def modifyRow(TableName, PkId, ListColumnToWrite, ListDataValueToWrite):
    Query=' '
    for i in range (0,len(ListColumnToWrite)-1):
        Query =Query + ListColumnToWrite[i]+ " = "+ ListDataValueToWrite[i] +", "
    i = len(ListColumnToWrite)-1
    Query =Query + ListColumnToWrite[i]+ " = "+ ListDataValueToWrite[i]
    print('querry', Query)
    querry ="UPDATE " + TableName + ' set'+ Query + " WHERE PkId = " + str(PkId) + " ;"
    print(querry)
    cur.execute(querry)
    con.commit()

def wStepperCmd(IpAdress, NoMotor, RegOrder, RegPosition, RegVelocity=1000):

    #Write a command to a stepper axis (BOCM)
    #IdEquipt: Ident of equipment to read
    # NoMotor: number of the motor on the equipment
    #CmdRegister: command register to write
    #SetpointPosition: Position setpoint
    #SetpointVelocity: Velocity setpoint
    
    IdEquipt = rEquipmentIdNbr(IpAdress)
    NoMod  = getSlotNumber(NoMotor)
    NoAxis = getAxisNumber(NoMotor)
    PkIdTbBoc = readPkModBim2BOC(IdEquipt, NoMod, NoAxis, FlgReadWrite=1) 
    
    UPDATE = 'UPDATE %s set RegOrder = %s, RegPosition = %s, RegVelocity = %s WHERE PkId =%s ' % ('TBBIM2BOC_1AXIS_W',str(RegOrder),str(RegPosition),str(RegVelocity),str(PkIdTbBoc))
    cur.execute(UPDATE)
    
    UPDATE = 'UPDATE  %s set cmd=1 WHERE PkId =%s ' % ('TBBIM2BOC_1AXIS_W',str(PkIdTbBoc)) # take write right
    cur.execute(UPDATE)
    con.commit()
    time.sleep(0.05) # ?? sinon ca marche pas ...
    
    UPDATE = 'UPDATE  %s set  Cmd = 0 WHERE PkId =%s ' % ('TBBIM2BOC_1AXIS_W',str(PkIdTbBoc)) # clear commande right
    cur.execute(UPDATE)
    con.commit()

def wStepperAckCmd(IpAdress, NoMotor): 
    #Acknowledgment of a command to a stepper axis (BOCM)
    #(Clear command registers in database)
    # IdEquipt: Ident of equipment to access
    # number of the motor on the equipment
    IdEquipt = rEquipmentIdNbr(IpAdress)
    NoMod  = getSlotNumber(NoMotor)
    NoAxis = getAxisNumber(NoMotor)
    PkIdTbBoc = readPkModBim2BOC(IdEquipt, NoMod, NoAxis, FlgReadWrite=1) 

    DB_CMD_None="0"
    DB_BOC_ORDER_NONE="0"
    ListColumnW = ["RegOrder"  , "RegPosition"    , "RegVelocity"    , "Cmd" ]
    ListValueW = [ DB_BOC_ORDER_NONE , "0" , "0" , DB_CMD_None ]
    RetFct = modifyRow("TBBIM2BOC_1AXIS_W", PkIdTbBoc, ListColumnW, ListValueW)

def rmove(IpAdress, NoMotor,posrelatif,vitesse=1000):
    # relative move of NoMotor 
    # posrelatif = position to move in step
    # SetpointPosition= str(posrelatif)
    # SetpointVelocity=str(vitesse)
    # wStepperCmd(IpAdress, NoMotor, CmdRegister, SetpointPosition, SetpointVelocity)
    # SELECT = 'select * from %s  where PkId=1 ' % 'TBBIM2BOC_1AXIS_W'
    # cur.execute(SELECT)
    # print('table write',cur.fetchall())
    # wStepperAckCmd(IpAdress, NoMotor)
    RegOrder = 3
    wStepperCmd(IpAdress, NoMotor, RegOrder, RegPosition=posrelatif,RegVelocity=vitesse)

def move(IpAdress, NoMotor,pos,vitesse=1000):
    # relative move of NoMotor 
    # posrelatif = position to move in step
    # SetpointPosition= str(posrelatif)
    # SetpointVelocity=str(vitesse)
    # wStepperCmd(IpAdress, NoMotor, CmdRegister, SetpointPosition, SetpointVelocity)
    # SELECT = 'select * from %s  where PkId=1 ' % 'TBBIM2BOC_1AXIS_W'
    # cur.execute(SELECT)
    # print('table write',cur.fetchall())
    # wStepperAckCmd(IpAdress, NoMotor)
    RegOrder = 2
    wStepperCmd(IpAdress, NoMotor, RegOrder, RegPosition=pos,RegVelocity=vitesse)

rmove('10.0.6.30', 1, 1000, vitesse=500)

SELECT = 'select * from %s  where PkId=1 ' % 'TBBIM2BOC_1AXIS_W'
cur.execute(SELECT)
print('table write',cur.fetchall())
# SELECT = 'select * from %s  WHERE PkId =1 ' % 'TBBIM2BOC_1AXIS_W'
# cur.execute(SELECT)
# print('table write',cur.fetchall())

# UPDATE = 'UPDATE %s set RegOrder = 3, RegPosition = -1000, RegVelocity = 500 WHERE PkId =1 ' % 'TBBIM2BOC_1AXIS_W'
# cur.execute(UPDATE)
# #con.commit()
# UPDATE = 'UPDATE %s set cmd=1 WHERE PkId =1 ' % 'TBBIM2BOC_1AXIS_W'
# cur.execute(UPDATE)
# a = con.commit()
# time.sleep(0.05)
# # SELECT = 'select * from %s  WHERE PkId =1 ' % 'TBBIM2BOC_1AXIS_W'
# # cur.execute(SELECT)

# # print('table write',cur.fetchall())
# # time.sleep(1)
# UPDATE = 'UPDATE %s set Cmd=0 WHERE PkId =1 ' % 'TBBIM2BOC_1AXIS_W'
# cur.execute(UPDATE)
# con.commit()
# SELECT = 'select * from %s  WHERE PkId =1 ' % 'TBBIM2BOC_1AXIS_W'
# cur.execute(SELECT)
# print('table write',cur.fetchall())
# SELECT = 'Select * from %s   WHERE PkId =1 ' % 'TBBIM2BOC_1AXIS_R'
# cur.execute(SELECT)
# print('posi',cur.fetchall())





def SetnameMoteur(IpAdress,NoMotor):
    IdEquipt = rEquipmentIdNbr(IpAdress)
    name=rStepperParameter(IdEquipt,NoMotor,listParaStr['nomAxe'])
    return name



# print('list eqp',rEquipmentList())
# print('nom moteur 2',nameMoteur('10.0.6.30',2))
# print('posi',rPositionMot(3 , 2))
# print('ref1',refName('10.0.6.30',1,1))#,RefValue('10.0.6.30',1,1))
# print('ref',rStepperParameter(3,1,1211))
# print('step',stepValue('10.0.6.30',1,1))
# print('butPlus',butLogPlusValue('10.0.6.30',1))
# print('list mot',listMotor('10.0.6.30'))
# print('name Equip : ',nameEquipment('10.0.6.30'))

# listCmd=["RegOrder"  , "RegPosition"    , "RegVelocity"    , "Cmd" ]
# listCmdValue=["3","2","1","4"]
# querry=''
# for i in range (0,len(listCmd)):
#     print(i)
#     print(querry)
#     querry =querry + listCmd[i]+ "= "+ listCmdValue[i] +" "
# print(querry)

con.close()




# SELECT = 'select * from %s  '% 'TbParameterSTR'
# # # # #PKID,IDMODULE,IDNAME,VALPARAM,NUMAXI,CATEGORY
# cur.execute(SELECT)

# IdEquipt = rEquipmentIdNbr('10.0.6.30')
# SELECT = 'select PkId from %s  where  IdEquipment= %s and NumSlot=-1'% ('TbModule',str(IdEquipt))   # list Pkid module
# cur.execute(SELECT)
# for row in cur :
#     a=row[0]
#     print(row[0])
# SELECT = 'select ValParam from %s where IDMODULE=17 and IDNAME=10 '% 'TbParameterSTR'
# cur.execute(SELECT)
# print(cur.fetchall())






# # #liste equipement :
# TABLE_NAME ='TbEquipment'
# SELECT = 'select * from %s  '% TABLE_NAME
# # #PKID,IDMODULE,IDNAME,VALPARAM,NUMAXI,CATEGORY
# cur.execute(SELECT)
# print(cur.fetchall())
# equip=[]
# typeEquip=[] # nb of ESBIM *2 = nb  of motors connected
# for row in cur:
#     equip.append(row[1])
#     typeEquip.append(row[2])
# print('IP rack connected',equip,'esbim type',typeEquip)
# # #IDNAME=10 : nom du rack

# #Liste nom Rack
# TABLE_NAME ='TbParameterSTR'
# SELECT = 'select * from %s where IDNAME=10  '% TABLE_NAME
# nomRack=[]
# cur.execute(SELECT)

# for row in cur:
#     nomRack.append(str(row[3]))
# print('name of the rack',nomRack)

# ## Liste nom moteur
# TABLE_NAME ='TbParameterSTR'
# SELECT = 'select * from %s where IDNAME=2  '% TABLE_NAME
# nomMoteur=[]
# cur.execute(SELECT)
# cur.execute('insert into TbParameterSTR (IDNAME) values ()') 
# print(cur.fetchall())
# for row in cur:
#     nomMoteur.append(str(row[3]))
# # print('motor name',nomMoteur)


# # liste pas dans l unite 

# TABLE_NAME ='TbParameterREAL'
# SELECT = 'select * from %s where IDNAME=1106  '% TABLE_NAME
# pasMoteur=[]
# cur.execute(SELECT)
# for row in cur:
#     pasMoteur.append(str(row[3]))
# # print('step value',pasMoteur)

# # liste  unite 

# TABLE_NAME ='TbParameterSTR'
# SELECT = 'select * from %s where IDNAME=1104  '% TABLE_NAME
# uniteMoteur=[]
# cur.execute(SELECT)
# for row in cur:
#     uniteMoteur.append(str(row[3]))
# # print('step name',uniteMoteur)





# # list   reference absolute 
# refName=["ref1Name","ref2Name","ref3Name","ref4Name","ref5Name","ref6Name"]
# TABLE_NAME ='TbParameterSTR'
# for u in range(0,6): 
#     value=1201+u
#     SELECT = 'select * from %s where IDNAME=%s '% (TABLE_NAME,str(value))
#     refName[u]=[]
#     cur.execute(SELECT)
    
#     #print (cur.fetchall())
#     for row in cur:
#         refName[u].append(str(row[3]))
        

# # liste value of reference position
# refPos=["ref1Pos","ref2Pos","ref3Pos","ref4Pos","ref5Pos","ref6Pos"]
# TABLE_NAME ='TbParameterREAL'
# for u in range(0,6): 
#     value=1211+u
#     SELECT = 'select * from %s where IDNAME=%s '% (TABLE_NAME,str(value))
#     refPos[u]=[]
#     cur.execute(SELECT)
   
#     for row in cur:
#         refPos[u].append(str(row[3]))



# #1009 Butée logicielle PLUS TbParameterINT
# #1010 Butée logicielle MOINS TbParameterINT

# # liste value of software butee +
# ButPlus=[]
# TABLE_NAME ='TbParameterINT'
# SELECT = 'select * from %s where IDNAME=%s '% (TABLE_NAME,str(1009))
# cur.execute(SELECT)
# for row in cur:
#     ButPlus.append(str(row[3]))



# # liste value of software logiciel butee-
# ButMoins=[]
# TABLE_NAME ='TbParameterINT'
# SELECT = 'select * from %s where IDNAME=%s '% (TABLE_NAME,str(1010))
# cur.execute(SELECT)
# for row in cur:
#     ButMoins.append(str(row[3]))


# #### Create a ini file with all the parameter

# for j in range (0,len(nomMoteur)):
#     # nomMoteur[j]=nomMoteur[j].lstrip()
#     if nomMoteur[j]==' ':
#         nomMoteur[j]='M'+str(j)
#     # nomMoteur[j]=nomMoteur[j].replace(' ','_'+str(j))
#     nomMoteur[j]=nomMoteur[j].replace(' ','_')
#     uniteMoteur[j]=uniteMoteur[j].replace('Â','')
#     if  pasMoteur[j]=='0.0':
#         pasMoteur[j]='1'
# # print(nomMoteur)
# conf=QtCore.QSettings('confMoteur.ini', QtCore.QSettings.Format.IniFormat)
# u=0
# for j in range (0,len(equip)):
#     # print('j=',j)
#     for i in range (0,typeEquip[j]*2):
#         # print(i+u)
#         conf.setValue(nomMoteur[i+u]+"/nom",nomMoteur[i+u])
#         conf.setValue(nomMoteur[i+u]+"/nomRack",nomRack[j])
#         conf.setValue(nomMoteur[i+u]+"/IPRack",equip[j])
#         conf.setValue(nomMoteur[i+u]+"/numESim",j)
#         conf.setValue(nomMoteur[i+u]+"/numMoteur",i+1)
#         print(nomMoteur[i+u], pasMoteur[i+u])
#         conf.setValue(nomMoteur[i+u]+"/stepmotor",1/float(pasMoteur[i+u]))
#         conf.setValue(nomMoteur[i+u]+"/unit",uniteMoteur[i+u])
#         conf.setValue(nomMoteur[i+u]+"/buteePos",ButPlus[i+u])
#         conf.setValue(nomMoteur[i+u]+"/buteeneg",ButMoins[i+u])
#         conf.setValue(nomMoteur[i+u]+"/moteurType","RSAI")
#         conf.setValue(nomMoteur[i+u]+"/rang",i+u)
#         for v in range(0,6):
#             conf.setValue(nomMoteur[i+u]+"/ref"+str(v)+"Name",refName[v][i+u])
#             conf.setValue(nomMoteur[i+u]+"/ref"+str(v)+"Pos",refPos[v][i+u])
#         conf.sync()
#     u=u+i+1
   




    
    
