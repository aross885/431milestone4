from rtlToAssemblyParser import writeARMInsn
from rtlToAssemblyParser import writeCodeLabel
from rtlToAssemblyParser import writeHeader
from rtlToAssemblyParser import createStack
from rtlToAssemblyParser import saveRegs
from rtlToAssemblyParser import readRTL
from rtlToAssemblyParser import freeStack
from rtlToAssemblyParser import restoreRegs
import sys

def access_RCT(regColTable, regNum, spillTable):
    #print(regNum)
    result = 0 
    if regNum == 0:
        result = regColTable[0]
        if result == 11:
            return 12
        return result
    if regNum == 1:
        result = regColTable[1]
        if result == 11:
            return 12
        return result
    if regNum == 2:
        result = regColTable[2]
        if result == 11:
            return 12
        return result
    if regNum == 3:
        result = regColTable[3]
        if result == 11:
            return 12
        return result
    if (regNum in spillTable.keys()):
        result = regColTable[spillTable[regNum][0] - 101]
    else:
        result = regColTable[regNum - 101]
    if result == 11:
        return 12
    return result


def setRegInsn(rtlFileName, line, lookupTable, mapTable, regColTable,spillTable, prevCallInsn, used):
    regnum = line[5][1][1]
    if ( regnum > 3 and regnum != 100):
        offset = lookupTable[regnum]
    elif (regnum == 100):
        offset = 0
    else:
        offset = 0
    if 'const_int' in line[5][2][0]:  #arent used in regtest 1 or 2
        access_num = access_RCT(regColTable, regnum, spillTable) #get the color of the virtual register
        text = "mov r"+ str(access_num)+", "+ str(line[5][2][1])  #move the const int into target reg
        text2 = "str r"+ str(access_num) +", [fp, #" + str(lookupTable[regnum]) + "]"  #store back into the original register that spilled location            
        DBtext2 = "str r"+ str(regnum) +", [fp, #" + str(lookupTable[regnum]) + "]"  #store back into the original register that spilled location            
        DBtext = "mov r"+ str(regnum)+", "+ str(access_RCT(regColTable, line[5][2][1], spillTable))
        writeARMInsn(rtlFileName, text)
        print(text) 
        print("DB: "+ DBtext)
        if regnum in spillTable.keys():            
            spillTable[regnum].pop(0) #pop off the virutal register we used
            writeARMInsn(rtlFileName, text2) #sinceit is spilled str it back in mem
            print(text2)
            print("DB: " + DBtext2)
    elif 'mem' in line[5][2][0]: #not used inr regtest1 or 2 
        print("MEM")  
        if 'virtual' in line[5][2][1][1][2]:
            access_num = access_RCT(regColTable, regnum, spillTable) 
            srcReg = line[5][2][1][2][1]
            print("SRCREG: "+ str(srcReg))
            text = "ldr r" + str(access_num) +", [fp, #" + str(lookupTable[srcReg]) + "]" #load srcReg mem location into Regnum
            DBtext = "ldr r" + str(regnum) +", [fp, #" + str(lookupTable[srcReg]) + "]" #lookup in maptable if srcreg is an offset
            writeARMInsn(rtlFileName, text)
            print(text)
            print("DB: "+ DBtext)
            if regnum in spillTable.keys():
                text2 = "str r"+ str(access_num) +", [fp, #" + str(lookupTable[regnum]) + "]" #store back to the homelocation of the spilt register             
                DBtext2 = "str r"+ str(regnum) +", [fp, #" + str(lookupTable[regnum]) + "]" #IS THIS IN THE TABLE??store back to the homelocation of the spilt register             
                spillTable[regnum].pop(0) #pop off the virtual register we used
                writeARMInsn(rtlFileName, text2)
                print(text2)
                print("DB: "+ DBtext2)
    elif ('plus' in line[5][2][0] or 'minus' in line[5][2][0] or 'mult' in line[5][2][0]):  
        arg1 = line[5][2][1][1]
        arg2 = line[5][2][2][1]
        offset1 = lookupTable[arg1] 
        text4 = ""
        arg1access = access_RCT(regColTable, arg1, spillTable)
        arg2access = arg2
        text = "ldr r"+ str(arg1access)+", [fp, #" + str(offset1) + "]"
        DBtext = "ldr r"+ str(arg1)+", [fp, #" + str(offset1) + "]" 
        access_num = access_RCT(regColTable, regnum, spillTable)
        if ("const_int" in line[5][2][2][0]): # adding constants
            text2 = "mov r"+ str(arg2)+", #" + str(line[5][2][2][1]) #
            DBtext2 = "mov r"+ str(arg2)+", #" + str(line[5][2][2][1])
        else: # adding registers
            offset2 = lookupTable[arg2]
            arg2access = access_RCT(regColTable, arg2, spillTable)
            DBtext2 = "ldr r"+ str(arg2access)+ ", [fp, #" + str(offset2) + "]"
            text2 = "ldr r"+ str(arg2access) + ", [fp, #" + str(offset2) + "]"
        if ('plus' in line[5][2][0]):
            if arg2 == arg2access:
                text3 = 'add r'+ str(access_num)+", r"+ str(arg1access)+", #"+ str(arg2access)
                DBtext3 = 'add r'+ str(regnum)+", r"+ str(arg1)+", #"+ str(arg2)            
            else :
                text3 = 'add r'+ str(access_num)+", r"+ str(arg1access)+", r"+ str(arg2access)
                DBtext3 = 'add r'+ str(regnum)+", r"+ str(arg1)+", r"+ str(arg2)            
        elif ('minus' in line[5][2][0]):
            if arg2 == arg2access:
                text3 = 'sub r'+ str(access_num)+", r"+ str(arg1access)+", #"+ str(arg2access)
                DBtext3 = 'sub r'+ str(regnum)+", r"+ str(arg1)+", #"+ str(arg2)            
            else :
                text3 = 'sub r'+ str(access_num)+", r"+ str(arg1access)+", r"+ str(arg2access)
                DBtext3 = 'sub r'+ str(regnum)+", r"+ str(arg1)+", r"+ str(arg2)            
        else:
            if arg2 == arg2access:
                text3 = 'mult r'+ str(access_num)+", r"+ str(arg1access)+", #"+ str(arg2access)
                DBtext3 = 'mult r'+ str(regnum)+", r"+ str(arg1)+", #"+ str(arg2)            
            else :
                text3 = 'mult r'+ str(access_num)+", r"+ str(arg1access)+", r"+ str(arg2access)
                DBtext3 = 'mult r'+ str(regnum)+", r"+ str(arg1)+", r"+ str(arg2)
        text4 = "str r"+ str(access_num)+", [fp, #" + str(offset) + "]"
        DBtext4 = "str r"+ str(regnum)+", [fp, #" + str(offset) + "]"
        if arg1 in spillTable.keys():   #will we only need to load before uses if they are spilled?
            writeARMInsn(rtlFileName, text)
            DBtext = "ldr r"+ str(arg1)+", [fp, #" + str(offset1) + "] spills to :" + str(spillTable[arg1])    
            spillTable[arg1].pop(0)
            #print(text)
            #print("DB: "+ DBtext )
        if arg2 in spillTable.keys():
            writeARMInsn(rtlFileName, text2)
            DBtext2 = "ldr r"+ str(arg2)+", [fp, #" + str(offset2) + "] spills to :" + str(spillTable[arg2])
            spillTable[arg2].pop(0)
            #print(text2)
            #print("DB: "+ DBtext2)
        writeARMInsn(rtlFileName, text3)
        used = 1
        #print(text3)
        #print("DB: "+ DBtext3)
        if regnum in spillTable.keys():
            writeARMInsn(rtlFileName, text4)
            #print(text4)
            #print("DB: "+ DBtext4)            
            spillTable[regnum].pop(0) #pop off the virutal register we used
    elif 'reg' in line[5][2][0]:
        if line[5][2][1] in spillTable.keys():
            offset1 = lookupTable[line[5][2][1]]
            text = "ldr r"+ str(access_RCT(regColTable, line[5][2][1], spillTable))+" [fp, #" + str(offset1) + "]"
            DBtext = "ldr r"+ str(line[5][2][1])+" [fp, #" + str(offset1) + "]"
            writeARMInsn(rtlFileName, text)
            #print(text)
            #print("DB: "+ DBtext)            
        if line[5][2][1] <= 15:
            text2 = "mov r"+ str(access_RCT(regColTable, regnum, spillTable))+", r"+ str(line[5][2][1])
            DBtext2 = "mov r"+ str(regnum)+", r"+ str(line[5][2][1])
            if '<retval>' in str(line):
                 text2 = "mov r0, r"+ str(line[5][2][1])
        else:
            text2 = "mov r"+ str(access_RCT(regColTable, regnum, spillTable))+", r"+ str(access_RCT(regColTable, line[5][2][1], spillTable))
            DBtext2 = "mov r"+ str(regnum)+", r"+ str(line[5][2][1])
            if '<retval>' in str(line):
                text2 = "mov r0, r"+ str(access_RCT(regColTable, line[5][2][1], spillTable))

        writeARMInsn(rtlFileName, text2)
        if regnum in spillTable.keys():
            text3 = "str r"+ str(access_RCT(regColTable, regnum, spillTable))+", [fp, #" + str(offset) + "]"
            DBtext3 = "str r"+ str(regnum)+", [fp, #" + str(offset) + "] spills to :" + str(spillTable[regnum][-1])
            used = 1
            spillTable[regnum].pop(0) #pop off the virtual register we used
            writeARMInsn(rtlFileName, text3)
            #print(text3)
            #print("DB: "+ DBtext3)
        
        #print(text2)
        #print("DB: "+ DBtext2)            
        
        if ("<retval>" in line[5][1]):
            text3 = "str r0, [fp, #" + str(offset) + "]"
            DBtext3 = "str r0, [fp, #" + str(offset) + "]"
            writeARMInsn(rtlFileName, text3)
            #print(text3)
            #print("DB: "+DBtext3)
    elif ("compare" in line[5][2][0]):
        #print("COMPARE")
        #print(line[5][2][1])
        offset1 = lookupTable[line[5][2][1][1]]
        text = "ldr r"+ str(access_RCT(regColTable, line[5][2][1][1], spillTable))+", [fp, #" + str(offset1) + "]"
        DBtext = "ldr r"+ str(line[5][2][1][1])+", [fp, #" + str(offset1) + "]"
        if line[5][2][1][1] in spillTable.keys():
            writeARMInsn(rtlFileName, text)
            spillTable[line[5][2][1][1]].pop(0)
            #print(text)
            #print("DB: " + DBtext)
        if ("const_int" in line[5][2][2][0]): # if constant
            text2 = "cmp r"+ str(access_RCT(regColTable, line[5][2][1][1], spillTable))+", #" + str(line[5][2][2][1])
            DBtext2 = "cmp r"+ str(line[5][2][1][1])+", #" + str(line[5][2][2][1])
            writeARMInsn(rtlFileName, text2)
            #print(text2)
            #print("DB: " + DBtext2)
        else: # else register
            offset2 = lookupTable[line[5][2][2][1]] 
            text2 = "ldr r"+ str(access_RCT(regColTable, line[5][2][2][1], spillTable))+", [fp, #" + str(offset2) + "]"  #ommit spilling str due to peep hole optimization???
            DBtext2 = "ldr r"+ str(line[5][2][2][1])+", [fp, #" + str(offset2) + "]"  #ommit spilling str due to peep hole optimization???
            text3 = "cmp r"+ str(access_RCT(regColTable, line[5][2][1][1], spillTable))+", r"+ str(access_RCT(regColTable, line[5][2][2][1], spillTable))
            DBtext3 = "cmp r"+ str(line[5][2][1][1])+", r"+ str(access_RCT(regColTable, line[5][2][2][1], spillTable))
            if line[5][2][2][1] in spillTable.keys():
                writeARMInsn(rtlFileName, text2)
                spillTable[line[5][2][2][1]].pop(0)
            writeARMInsn(rtlFileName, text3)
            #print(text2)
            #print("DB: " + DBtext2)
            #print(text3)
            #print("DB: " + DBtext3)
    if prevCallInsn == 1 and used == 1:
        prevCallInsn = 0
        used = 0
        popregs = "pop {r0, r1, r2, r3}"
        #writeARMInsn(rtlFileName, popregs)
        
    
    return prevCallInsn






def jumpInsn(rtlFileName, line, prevCallInsn):
    if ("label_ref" in line[5][2][0]):
        # unconditional jump
        if (str(line[5][2][1]) == "main"):
            text = "b " + str(line[5][2][1])
        else:
            text = "b L" + str(line[5][2][1])
    elif ("if_then_else" in line[5][2][0]):
        # conditional jump
        condition = str(line[5][2][1][0])
        if (str(line[5][2][2][1]) == "main"):
            text = "b" + condition + " " + str(line[5][2][2][1])
        else:
            text = "b" + condition + " L" + str(line[5][2][2][1])
    writeARMInsn(rtlFileName, text)
    #print(text)
    prevCallInsn = 0
    return prevCallInsn



def codeLabel(rtlFileName, line):
    if (str(line[1]) == "main"):
        writeCodeLabel(rtlFileName, str(line[1]))
    else:
        writeCodeLabel(rtlFileName, "L" + str(line[1]))
        #print("L" + str(line[1]) + ":")
    


def setMemInsn(rtlFileName, line, lookupTable, mapTable, regColTable, spillTable, prevCallInsn):
    offset = line[5][1][1][2][1]
    regToSave = line[5][-1][1]
    text3 = ""
    if (offset in mapTable):
        access_num = access_RCT(regColTable, mapTable[offset], spillTable)
        text3 = "str r" + str(access_num) +", [sp, #" + str(lookupTable[mapTable[offset]]) + "]"
        DBtext3 = "str r" + str(mapTable[offset]) +", [sp, #" + str(lookupTable[mapTable[offset]]) + "]"
    else:
        mapTable[offset] = regToSave
    text = "ldr r"+ str(access_RCT(regColTable, regToSave, spillTable))+ " , [sp, #" + str(lookupTable[regToSave]) + "]"
    DBtext = "ldr r"+ str(regToSave)+ " , [sp, #" + str(lookupTable[regToSave]) + "]"
    text2 = "str r"+ str(access_RCT(regColTable, regToSave, spillTable))+ " , [sp, # "+ str(lookupTable[regToSave]) + "]"
    DBtext2 = "str r"+ str(regToSave)+ " , [sp, # "+ str(lookupTable[regToSave]) + "]"
    writeARMInsn(rtlFileName, text)
    writeARMInsn(rtlFileName, text2)
    #print(text)
    #print("DB: " + DBtext)
    #print(text2)
    #print("DB: " + DBtext2)


    if (text3 != ""):
        writeARMInsn(rtlFileName, text3)
       # print(text3)
        #print("DB: " + DBtext3)
    prevCallInsn = 0
    return prevCallInsn


def callInsn(rtlFileName, line, prevCallInsn):
    func = line[5][2][2][1][1][1][0]
    pushregs = "push {r0, r1, r2, r3}"
    text = "bl " + str(func)
    #writeARMInsn(rtlFileName, pushregs)
    writeARMInsn(rtlFileName, text)
    #writeARMInsn(rtlFileName, popregs)
    #print(line[1])
    #print(text)
    prevCallInsn = 1
    return prevCallInsn



def parseRTLtoAssembly(rtlFileName, lookupTable, regColTable, spillTable):
    rtlInput = readRTL(rtlFileName)
    lineCount = 0
    mapTable = {}
    insns = []
    prevCallInsn = 0
    used = 0
    for line in rtlInput:
        if (lineCount == 2):
            # create header
            writeHeader(rtlFileName, line)
            saveRegs(rtlFileName)
            createStack(rtlFileName, len(regColTable) - 4) 
        lineCount += 1
        if type(line) == list:       
            #print(line[1])
            if line[0] == 'insn':
                if line[5][0] == 'set':
                    if 'reg' in line[5][1][0]:
                        prevCallInsn  = setRegInsn(sys.argv[1], line, lookupTable, mapTable, regColTable, spillTable, prevCallInsn, used)
                    elif 'mem' in line[5][1][0]:
                        prevCallInsn = setMemInsn(sys.argv[1], line, lookupTable, mapTable, regColTable, spillTable, prevCallInsn)
            elif line[0] == 'jump_insn':
                prevCallInsn = jumpInsn(rtlFileName, line, prevCallInsn)
            elif line[0] == 'call_insn':
                prevCallInsn  = callInsn(rtlFileName,line, prevCallInsn)
            elif line[0] == 'code_label':
                codeLabel(rtlFileName, line)
    freeStack(rtlFileName, len(regColTable) - 4)
    restoreRegs(rtlFileName)
                
