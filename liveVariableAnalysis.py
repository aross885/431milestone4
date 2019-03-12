# CPE 431: Milestone 3
# John Luu

import controlFlowGraph

# Calculates all the live ins and outs for each basic block and stores them in the cfg passed in
# Input: cfg that contains defs and uses
# Output: updated cfg (not returned, but the cfg inside is altered)
def livenessAnalysis(cfg):
    numVirtRegs = cfg.numVirtRegs
    changedInSet = True
    liveOut = [None] * (numVirtRegs + 4)
    while (changedInSet):
        changedInSet = False
        for b in range(len(cfg.blocks)):
            liveOut = calculateLiveOut(b, cfg.blocks, cfg.edges)
            liveIn = calculateLiveIn(b, liveOut, cfg.blocks)
            if (liveIn != cfg.blocks[b].liveIns):
                changedInSet = True
            cfg.blocks[b].liveIns = liveIn
            cfg.blocks[b].liveOuts = liveOut


# Calculates the live outs for a given basic block
# Input: the basic block number, all the basic blocks, and all the edges
# Output: the live outs for the current basic block
def calculateLiveOut(blockNum, blocks, edges):
    # union all the successors of the block IN(B)
    successors = findSuccessors(blockNum, edges)
    successorsLists = []
    if (len(successors) == 0):
        return [0] * len(blocks[0].liveIns)
    for successor in successors:
        successorsLists.append(blocks[successor].liveIns)
    return listUnion(successorsLists)


# Calculates the live ins for a given basic block
# Input: the basic block number, the live out list of the current basic block, and all the basic blocks
# Output: the live ins of the current basic block
def calculateLiveIn(blockNum, liveOutList, nodes):
    convertedArray = liveOutList.copy()
    for insn in reversed(nodes[blockNum].insns):
        curDefs = insn.defs
        curUses = insn.uses
        for i in range(len(curDefs)):
            curdef = curDefs[i]
            if (curdef >= 105):
                curdef = curdef - 101 # save room for r0-r3, r105 starts at index 4 (position 5)
            if (convertedArray[curdef] == 1):
                convertedArray[curdef] = 0
        for i in range(len(curUses)):
            curuse = curUses[i]
            if (curuse >= 105):
                curuse = curuse - 101  # save room for r0-r3, r105 starts at index 4 (position 5)
            if (convertedArray[curuse] == 0):
                convertedArray[curuse] = 1
    return convertedArray


# Finds all the successors of a basic block
# Input: the block number and the list of edges
# Output: the list of successors
def findSuccessors(blockNum, edges):
    successors = []
    for i in range(len(edges[blockNum])):
        if (edges[blockNum][i] == 1):
            successors.append(i)
    return successors


# Unions a list of lists together
# Input: a list of lists
# Output: the unioned list
def listUnion(listsToUnion):
    if (len(listsToUnion) == 0):
        return []
    elif (len(listsToUnion) == 1):
        return listsToUnion[0]
    else:
        count = 0
        temp = []
        while (count < len(listsToUnion) - 1):
            temp = listsToUnion[count]
            temp = union(temp, listsToUnion[count + 1])
            count += 1
        return temp


# Assuming the two input lists are filled with 0's and 1's only, does a bitwise and of the two lists
# Input: two lists of the same length to union
# Output: final unioned list
def union(list1, list2):
    # check if the two input lists are the same length
    if (len(list1) == len(list2)):
        union = [None] * len(list1)
        for i in range(len(list1)):
            if (list1[i] == 1 or list2[i] == 1):
                union[i] = 1
            else:
                union[i] = 0
        return union
    else:
        return []