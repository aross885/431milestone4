import sys
import sexpParser
import os
from rtlToAssemblyParser import readRTL
from rtlToAssemblyParser import findMaxReg
from rtlToAssemblyParser import createLookupTable
from collections import OrderedDict
import controlFlowGraph as cf
import liveVariableAnalysis as lva
import interferenceGraph as ig
import graphColorizer as gc
import m3toAssembly as m3a
import milestone4 as m4
import LSDAG as ls


def addtouses(regnum ,defs, uses):
    if regnum in defs:
        return uses
    else:
        uses.add(regnum)
        return uses
#add regnum to defs
#look for uses
def setRegInsnIG(line, defs, uses):
    regnum = line[5][1][1]
    iDefs = []
    iUses = []
    if 'mem' in line[5][2][0]:
        if 'virtual' in line[5][2][1][1][2]:
            uses = addtouses(line[5][2][1][1][1], defs, uses)
            iUses.append(line[5][2][1][1][1])
    elif ('plus' in line[5][2][0] or 'minus' in line[5][2][0] or 'mult' in line[5][2][0]):
        arg1 = line[5][2][1][1]
        if 'const_int' in str(line[5][2]):
            uses = addtouses(arg1, defs, uses)
            iUses.append(arg1)
        else:
            arg2 = line[5][2][2][1]
            uses = addtouses(arg1, defs, uses)
            uses = addtouses(arg2, defs, uses)
            iUses.append(arg1)
            iUses.append(arg2)
    elif 'reg' in line[5][2][0]:
        uses = addtouses(line[5][2][1], defs, uses)
        iUses.append(line[5][2][1])
        #if ("<retval>" in str(line[5][2])):
        #   uses = addtouses(line[5][2][1], defs, uses)
        #  iUses.append(line[5][2][1])
    elif ("compare" in line[5][2][0]):
        uses = addtouses(line[5][2][1][1], defs, uses)
        iUses.append(line[5][2][1][1])
        if ("const_int" not in line[5][2][2][0]): # if constant
            uses = addtouses(line[5][2][2][1],defs, uses)
            iUses.append(line[5][2][2][1])
    if regnum != 100:
        defs.add(regnum)
        iDefs.append(regnum)
    if 100 in iUses:
        iUses.remove(100)
    return cf.Insn(iDefs, iUses)

def setMemInsnIG(line, defs, uses):
    regToSave = line[5][-1][1]
    #print("SET MEM " " " + str(regToSave))
    uses = addtouses(regToSave, defs, uses)
    iUses = []
    if regToSave != 100:
        iUses.append(regToSave)
    return cf.Insn([], iUses)


def jumpInsnIG(rtlfilename, line, neighbors):
    if ("label_ref" in line[5][2][0]):
        # unconditional jump
        neighbors.add(getbasicblocknum(rtlfilename, line[5][2][1]))
    elif ("if_then_else" in line[5][2][0]):
        # conditional jump
        condition = str(line[5][2][1][0])
        neighbors.add(getbasicblocknum(rtlfilename, line[5][2][2][1]))


def getbasicblocknum(rtlfilename, insnnum):
    rtlInput = readRTL(rtlfilename)
    for line in rtlInput:
        if type(line) == list:       #for code labels
            if line[0] == 'note':
                if line[2] == insnnum:
                    return line[4]

def parseRTLtoIG(rtlFileName, numVirtRegs):
    rtlInput = readRTL(rtlFileName)
    lineCount = 0
    mapTable = {}
    defs = set()
    uses = set()
    neighbors = set()
    insns = []
    curbb = 1
    VertList = []
    #print(rtlInput)
    for line in rtlInput:
        if type(line) == list:
            if line[0] == 'insn':
                if line[4] != curbb:
                    if curbb == 1:
                        curbb = line[4]
                        if line[5][0] == 'set':
                            if 'reg' in line[5][1][0]:
                                insns.append(setRegInsnIG(line, defs, uses))
                            elif 'mem' in line[5][1][0]:
                                insns.append(setMemInsnIG(line, defs, uses))
                        continue
                    neighbors.add(line[4])
                    VertList.append(cf.BasicBlock(curbb, defs, uses, neighbors, insns, numVirtRegs))
                    defs = set()
                    uses = set()
                    neighbors = set()
                    insns = []
                    curbb = line[4]
                if line[5][0] == 'set':
                    if 'reg' in line[5][1][0]:
                        insns.append(setRegInsnIG(line, defs, uses))
                    elif 'mem' in line[5][1][0]:
                        insns.append(setMemInsnIG(line, defs, uses))
            elif line[0] == 'jump_insn':
                jumpInsnIG(rtlFileName, line, neighbors)
            elif line[0] == 'code_label':
                mybb = getbasicblocknum(rtlFileName ,line[1])
                neighbors.add(mybb)
            elif line[0] == 'call_insn':
                insns.append(cf.Insn([0,1,2,3], []))

    VertList.append(cf.BasicBlock(curbb, defs, uses, neighbors, insns, numVirtRegs))
    return VertList

def construct_AM(vertexList):
    adjMat = []
    vertnumToAdjMatInd = OrderedDict()
    ind = 0
    for i in range(len(vertexList)):
        adjMat.append([0 for i in range(len(vertexList))])
    for vert in vertexList:
        vertnumToAdjMatInd[vert.bbnum] =  ind
        ind += 1
    for vert in vertexList:
        for neighb in vert.neighbors:
            adjMat[access_AM(vert.bbnum, vertnumToAdjMatInd)][access_AM(neighb, vertnumToAdjMatInd)] =1
            adjMat[access_AM(neighb, vertnumToAdjMatInd)][access_AM(vert.bbnum, vertnumToAdjMatInd)] =1
    return [adjMat, vertnumToAdjMatInd]

def access_AM(bbnum, vertnumToAdjMatInd):
    return vertnumToAdjMatInd[bbnum]

def constructCFG(rtlFileName):
    maxReg = findMaxReg(rtlFileName)
    # print(maxReg)
    result = parseRTLtoIG(rtlFileName, maxReg - 104)
    #  for res in result:
    #     print(str(res.bbnum) + " DEFS " + str(res.defs) + " USES " + str(res.uses) + " NEIGHBORS " + str(res.neighbors))
    #    for ins in res.insns:
    #       print("def "+ str(ins.defs) + " uses " + str(ins.uses)

    unpack = (construct_AM(result))
    adjMatrix = unpack[0]
    vertnumToAdjMatInd = unpack[1]
    # for line in adjMatrix:
    #    print(str(line))
    cfg = cf.CFG(result, adjMatrix, maxReg -104)
    return cfg


def main():
    if (len(sys.argv) != 2):
        sys.stderr.write("Usage: python miletsone3.py <filename>\n")
        exit(1)
    maxReg = findMaxReg(sys.argv[1])
    # minReg = findMinReg(sys.argv[1])
    lookupTable = createLookupTable(maxReg)

    #print("STEP 0: Constructing CFG...")
    cfg = constructCFG(sys.argv[1])
    #print("STEP 1: Performing Live Variable Analysis...")
    lva.livenessAnalysis(cfg)
    #print("STEP 2: Building Interference Graph...")
    ifg = ig.buildInterferenceGraph(cfg)

    #print("\nInterference Graph")
    #for i in range(len(ifg)):
        #print(ifg[i])

    #print("\nSTEP 3: Coloring Graph...")
    cfg, colors = gc.colorGraph(cfg, ifg)
    #print("\nColors: ")
    #print(colors)

    #print("\nSpill Table")
    #for key in cfg.spillTable.keys():
        #print("Register: {} - Spilled To: {}".format(key, cfg.spillTable[key]))

    #for key in cfg.spillTable.keys():
     #   for value in cfg.spillTable[key]:
      #      color = colors[value - 101]
       #     print("Register: {} - Spilled To: {} Color: {}".format(key, value, color))

    #for block in cfg.blocks:
        #print(block.bbnum)
        #for insn in block.insns:
            #print("Defs: {} Uses: {}".format(insn.defs, insn.uses))
            
    m3a.parseRTLtoAssembly(sys.argv[1], lookupTable, colors, cfg.spillTable)

    LSDAG = m4.create_LSDAG(cfg)
    
    for ins in LSDAG.insns:
        print(ins.defs, ins.uses)
    for i in range(len(LSDAG.edges)):
        print(LSDAG.edges[i])
    

if __name__ == "__main__":
    main()