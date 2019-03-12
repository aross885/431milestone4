import sys
import sexpParser
import os


# reads file in as RTL by parsing as an s-expression
# Input: name of file (should be format of <fileName>.c.212r.expand)
# Output: file descriptor that can be iterated through
def readRTL(rtlFileName):
    rtlFile = open(rtlFileName, "r")
    rtl = rtlFile.read()
    rtl = "(" + rtl + ")"
    rtlInput = sexpParser.parse_sexp(rtl)
    return rtlInput


def setRegInsn(rtlFileName, line, maxreg, lookupTable, mapTable):
    regnum = line[5][1][1]
    if (regnum > 15 and regnum != 100):
        offset = lookupTable[regnum]
    elif (regnum == 100):
        offset = 0
    else:
        offset = 0
    if 'const_int' in line[5][2][0]:
        text = "mov r0, #" + str(line[5][2][1])
        text2 = "str r0, [fp, #" + str(offset) + "]"
        writeARMInsn(rtlFileName, text)
        writeARMInsn(rtlFileName, text2)
    elif 'mem' in line[5][2][0]:
        if 'virtual' in line[5][2][1][1][2]:
            text = "ldr r0, [fp, #" + str(
                lookupTable[mapTable[line[5][2][1][2][1]]]) + "]"
            text2 = "str r0, [fp, #" + str(offset) + "]"
            writeARMInsn(rtlFileName, text)
            writeARMInsn(rtlFileName, text2)
    elif ('plus' in line[5][2][0] or 'minus' in line[5][2][0] or 'mult' in line[5][2][0]):
        arg1 = line[5][2][1][1]
        arg2 = line[5][2][2][1]
        offset1 = lookupTable[arg1]
        text = "ldr r1, [fp, #" + str(offset1) + "]"
        if ("const_int" in line[5][2][2][0]): # adding constants
            text2 = "mov r2, #" + str(line[5][2][2][1])
        else: # adding registers
            offset2 = lookupTable[arg2]
            text2 = "ldr r2, [fp, #" + str(offset2) + "]"

        if ('plus' in line[5][2][0]):
            text3 = 'add r0, r1, r2'
        elif ('minus' in line[5][2][0]):
            text3 = 'sub r0, r1, r2'
        else:
            text3 = 'mul r0, r1, r2'
        text4 = "str r0, [fp, #" + str(offset) + "]"
        writeARMInsn(rtlFileName, text)
        writeARMInsn(rtlFileName, text2)
        writeARMInsn(rtlFileName, text3)
        writeARMInsn(rtlFileName, text4)
    elif 'reg' in line[5][2][0]:
        offset1 = lookupTable[line[5][2][1]]
        text = "ldr r1, [fp, #" + str(offset1) + "]"
        text2 = "mov r0, r1"
        writeARMInsn(rtlFileName, text)
        writeARMInsn(rtlFileName, text2)
        if ("<retval>" in line[5][1]):
            text3 = "str r0, [fp, #" + str(offset) + "]"
            writeARMInsn(rtlFileName, text3)
    elif ("compare" in line[5][2][0]):
        offset1 = lookupTable[line[5][2][1][1]]
        text = "ldr r1, [fp, #" + str(offset1) + "]"
        writeARMInsn(rtlFileName, text)
        if ("const_int" in line[5][2][2][0]): # if constant
            text2 = "cmp r1, #" + str(line[5][2][2][1])
            writeARMInsn(rtlFileName, text2)
        else: # else register
            offset2 = lookupTable[line[5][2][2][1]]
            text2 = "ldr r2, [fp, #" + str(offset2) + "]"
            text3 = "cmp r1, r2"
            writeARMInsn(rtlFileName, text2)
            writeARMInsn(rtlFileName, text3)



def jumpInsn(rtlFileName, line):
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


def codeLabel(rtlFileName, line):
    if (str(line[1]) == "main"):
        writeCodeLabel(rtlFileName, str(line[1]))
    else:
        writeCodeLabel(rtlFileName, "L" + str(line[1]))


def setMemInsn(rtlFileName, line, maxReg, lookupTable, mapTable):
    offset = line[5][1][1][2][1]
    regToSave = line[5][-1][1]
    text3 = ""
    if (offset in mapTable):
        text3 = "str r1, [fp, #" + str(lookupTable[mapTable[offset]]) + "]"
    else:
        mapTable[offset] = regToSave
    text = "ldr r1, [fp, #" + str(lookupTable[regToSave]) + "]"
    text2 = "str r1, [fp, #" + str(lookupTable[regToSave]) + "]"
    writeARMInsn(rtlFileName, text)
    writeARMInsn(rtlFileName, text2)
    if (text3 != ""):
        writeARMInsn(rtlFileName, text3)



def callInsn(rtlFileName, line):
    func = line[5][2][1][1][1][0]
    text = "bl " + str(func)
    writeARMInsn(rtlFileName, text)



# main parse function to convert RTL into ARM assembly insns
# Input: name of file (should be format of <fileName>.c.212r.expand)
# Output: nothing
def parseRTLtoAssembly(rtlFileName, numVirtRegs):
    rtlInput = readRTL(rtlFileName)
    maxReg = numVirtRegs + 104
    lineCount = 0

    lookupTable = createLookupTable(maxReg)
    mapTable = {}

    for line in rtlInput:
        if (lineCount == 2):
            # create header
            writeHeader(rtlFileName, line)
            saveRegs(rtlFileName)
            createStack(rtlFileName, numVirtRegs)
        lineCount += 1
        if type(line) == list:
            print(line)
            if line[0] == 'insn':
                if line[5][0] == 'set':
                    if 'reg' in line[5][1][0]:
                        setRegInsn(rtlFileName, line, maxReg, lookupTable, mapTable)
                    elif 'mem' in line[5][1][0]:
                        setMemInsn(rtlFileName, line, maxReg, lookupTable, mapTable)
            elif line[0] == 'call_insn':
                callInsn(rtlFileName, line)
            elif line[0] == 'code_label':
                codeLabel(rtlFileName, line)
            elif line[0] == 'jump_insn':
                jumpInsn(rtlFileName, line)
    freeStack(rtlFileName, numVirtRegs)
    restoreRegs(rtlFileName)


# creates the ARM assembly file, and writes a header for it
# Input: name of file (should be format of <fileName>.c.212r.expand)
# Output: nothing
def writeHeader(rtlFileName, text):
    writeToFile(rtlFileName, "	.arch armv6", "w")
    writeToFile(rtlFileName, "	.text", "a")
    writeToFile(rtlFileName, "	.global " + str(text), "a")
    writeCodeLabel(rtlFileName, text)


# writes a code label to the file
# Input: name of file (should be format of <fileName>.c.212r.expand)
# Output: nothing
def writeCodeLabel(rtlFileName, codeLabel):
    writeToFile(rtlFileName, str(codeLabel) + ":", "a")

# returns the number of the largest register used
# Input: name of the file (should be format of <fileName>.c.212r.expand)
# Output: the highest register # used
def findMaxReg(rtlFileName):
    rtlInput = readRTL(rtlFileName)
    maxReg = 0
    for l in rtlInput:
        line = str(l)
        if "reg:SI" in line:
            regindex = line.index("reg:SI")
            strnum = line[regindex + 8 : regindex + 12]
            try:
                intnum = int(strnum)
                if intnum > maxReg:
                    maxReg = intnum
            except ValueError:
                continue
        if "reg:QI" in line:
            regindex = line.index("reg:QI")
            strnum = line[regindex + 8 : regindex + 12]
            try:
                intnum = int(strnum)
                if intnum > maxReg:
                    maxReg = intnum
            except ValueError:
                continue
        if "reg/f:SI" in line:
            regindex = line.index("reg/f:SI")
            strnum = line[regindex + 10 : regindex + 14]
            try:
                intnum = int(strnum)
                if intnum > maxReg:
                    maxReg = intnum
            except ValueError:
                continue
    return maxReg


# general function for writing to a file with the removal of the extensions (.c.212r.expand)
# Input: name of file (should be format of <fileName>.c.212r.expand)
#        text to write
#        file open parameter ("w" for write, "a" for append)
# Output: nothing
def writeToFile(rtlFileName, text, parameter):
    # checks if the rtl filename is valid
    if (rtlFileName.count(".") < 3):
        raise Exception("Invalid file type, should be of <filename>.c.212r.expand\n")

    # removes the .expand extension
    fileName212r, fileExtension212r = os.path.splitext(rtlFileName)
    # removes the .212r extension
    fileNameC, fileExtensionC = os.path.splitext(fileName212r)
    # removes the .c extension
    fileNameOnly, fileExtensionOnly = os.path.splitext(fileNameC)

    # opens a file and appends the .s extension
    fileOutput = open(fileNameOnly + ".s", parameter)
    fileOutput.write(str(text) + "\n")


# writes an ARM instruction to a file
# Input: name of file (should be format of <fileName>.c.212r.expand)
#        text to write
# Output: nothing
def writeARMInsn(rtlFileName, text):
    writeToFile(rtlFileName, "	" + text, "a")


# writes the ARM instruction to save the caller's registers (fp and lr)
# Input: name of file (should be format of <fileName>.c.212r.expand)
# Output: nothing
def saveRegs(rtlFileName):
    writeARMInsn(rtlFileName, "push {r4, r5, r6, r7, r8, r9, r10, fp, r12, lr}")


# writes the ARM instruction to restore the caller's registers (fp and pc)
# Input: name of file (should be format of <fileName>.c.212r.expand)
# Output: nothing
def restoreRegs(rtlFileName):
    writeARMInsn(rtlFileName, "pop {r4, r5, r6, r7, r8, r9, r10, fp, r12, pc}")


# create a stack to keep track of virtual registers
# Input: name of file (should be format of <fileName>.c.212r.expand)
#        number of virtual registers to allocate
# Output: nothing
def createStack(rtlFileName, size):
    stackSize = size * 4
    writeARMInsn(rtlFileName, "mov fp, sp")
    writeARMInsn(rtlFileName, "sub sp, sp, #" + str(stackSize))


# frees the stack
# Input: name of file (should be format of <fileName>.c.212r.expand)
#        number of virtual registers that have been allocated
# Output: nothing
def freeStack(rtlFileName, size):
    stackSize = size * 4
    writeARMInsn(rtlFileName, "add sp, sp, #" + str(stackSize))
    writeARMInsn(rtlFileName, "mov sp, fp")


#calculates the offset for a given register given the register number and the maximum register number of the program
#offset is from the stack pointer, the highest register number is stored below the link register
# SP + OFFSET
""" fp
    lr
    118
    117
    .
    .
    .
    105
    sp"""
def calc_offset(regnum, maxRegNum):
    return ((maxRegNum - 104) * 4) - ((maxRegNum - regnum + 1) * 4)


def createLookupTable(maxRegNum):
    lookupTable = {}
    offset = -4
    for i in range(maxRegNum, 104, -1):
        lookupTable[i] = offset
        offset -= 4
    return lookupTable

# main function that is called when the program is run
# Input: nothing
# Output: nothing
def main():
    # command line args checker
    if (len(sys.argv) != 2):
        sys.stderr.write("Usage: python rtlToAssemblyParser.py <filename>\n")
        exit(1)

    maxReg = findMaxReg(sys.argv[1])

    parseRTLtoAssembly(sys.argv[1], maxReg - 104)

if __name__ == '__main__':
    main()