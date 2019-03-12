# CPE 431: Milestone 3
# John Luu

import spilling
import liveVariableAnalysis
import interferenceGraph as ig
import controlFlowGraph

# Generates the array of colours used for register allocation
# Input: the cfg after the live ins and live outs are calculated during the live variable analysis, and the complete interference graph
# Output: the updated cfg with the spill table and the array of colours used for register allocation (in the order of r0, r1, r2, r3, r105, ..., maxVirtualRegisterNumber)
def colorGraph(cfg, interferenceGraph):

    # hardcoded to 12, r0 - r12 excluding r11
    numColors = 12

    # empty array to store the colours to output (in the order of r0, r1, r2, r3, r105, ..., maxVirtualRegisterNumber)
    virtRegColors = [-1] * len(interferenceGraph)

    # a stack that contains the order in which the registers should be looked at during colouring
    stack = createStack(interferenceGraph)

    # while the stack exists, generate the colours
    while (len(stack) > 0):
        usedColors = []
        reg = stack.pop() - 101
        currentRegsList = createCurrentRegsList(virtRegColors)
        curColor = 4

        # check for interferences with the existing coloured graph
        for i in range(len(currentRegsList)):
            if (interferenceGraph[reg][currentRegsList[i]] == 1):
                usedColors.append(virtRegColors[currentRegsList[i]])
                curColor = getColor(usedColors)

        # check if you run out of colours, if you do, spill
        if (curColor >= numColors):
            # spill here, bc not enough colours
            cfg = spilling.spill(cfg)
            liveVariableAnalysis.livenessAnalysis(cfg)
            curIg = ig.buildInterferenceGraph(cfg)
            returnColors = colorGraph(cfg, curIg)
            return returnColors

        # otherwise, colour the node
        else:
            virtRegColors[reg] = curColor

    # print("\nSpill Table")
    # for key in cfg.spillTable.keys():
    #     print("Register: {} - Spilled To: {}".format(key, cfg.spillTable[key]))

    return cfg, virtRegColors


# Simplifies the interference graph to create a stack of registers to pop from for colouring
# Input: the complete interference graph
# Output: a stack that contains the order in which the registers should be looked at during colouring
def createStack(interferenceGraph):
    numColors = 12
    stack = []
    interferenceGraphCopy = interferenceGraph.copy()
    reset = False
    optimisticChoose = False
    i = 4

    # put all the registers onto the stack, using the simplify method for order
    while (len(stack) < len(interferenceGraphCopy) - 4):
        if (reset):
            i = 4
            reset = False
        if (i == len(interferenceGraphCopy) - 1):
            reset = True
            optimisticChoose = True
        if (i not in stack):
            reset = False

            # optimistically choose one if necessary
            if (optimisticChoose):
                stack.append(i)
                interferenceGraphCopy[i] = [0] * len(interferenceGraph[i])
                for j in range(len(interferenceGraphCopy)):
                    interferenceGraphCopy[j][i] = 0
                reset = True
                optimisticChoose = False
            elif (getDegree(interferenceGraphCopy, i) <= numColors):
                stack.append(i)
                interferenceGraphCopy[i] = [0] * len(interferenceGraph[i])
                for j in range(len(interferenceGraphCopy)):
                    interferenceGraphCopy[j][i] = 0
                reset = True
        i += 1

    # adds all the real registers first
    for i in range(3, -1, -1):
        stack.append(i)
        interferenceGraphCopy[i] = [0] * len(interferenceGraph[i])
        for j in range(len(interferenceGraphCopy)):
            interferenceGraphCopy[j][i] = 0

    # alter the values to account for the numerical offset
    for i in range(len(stack)):
        stack[i] = stack[i] + 101

    return stack


# Gets the degree of any node in the graph
# Input: the adjacency matrix of the graph, and the number of the node you want to find the degree of
# Output: the degree of the node in the graph
def getDegree(adjMat, degreeOf):
    degree = 0
    for i in range(len(adjMat[degreeOf])):
        if (adjMat[degreeOf][i] == 1):
            degree += 1
    return degree


# Creates a list of the registers that have been coloured already
# Input: list of the colours (in the order of r0, r1, r2, r3, r105, ..., maxVirtualRegisterNumber)
# Output: list of the registers that have been coloured already
def createCurrentRegsList(virtRegColors):
    currentRegs = []
    for i in range(len(virtRegColors)):
        if (virtRegColors[i] != -1):
            currentRegs.append(i)
    return currentRegs


# Gets the correct colour that doesn't interfere
# Input: the list of colours that have been used already
# Output: the correct colour available
def getColor(usedColors):
    i = 4
    while (i in usedColors):
        i += 1
    return i