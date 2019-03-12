# CPE 431: Milestone 3
# John Luu

import controlFlowGraph

# Builds the interference graph using the cfg that was updated with the live ins and outs for each basic block
# Input: cfg that was updated with the live ins and outs from the live variable analysis algorithms
# Output: the complete interference graph generated from those live variables
def buildInterferenceGraph(cfg):
    numVirtRegs = cfg.numVirtRegs
    interferenceGraph = [[0 for x in range(numVirtRegs + 4)] for y in range(numVirtRegs + 4)]
    for block in cfg.blocks:
        for i in range(len(block.liveIns)):
            for j in range(i + 1, len(block.liveIns)):
                if (block.liveIns[i] == 1 and block.liveIns[j] == 1):
                    interferenceGraph[i][j] = 1
                    interferenceGraph[j][i] = 1
        for i in range(len(block.liveOuts)):
            for j in range(i + 1, len(block.liveOuts)):
                if (block.liveOuts[i] == 1 and block.liveOuts[j] == 1):
                    interferenceGraph[i][j] = 1
                    interferenceGraph[j][i] = 1
        interferenceGraph = addSingleBlockInterferences(interferenceGraph, cfg.blocks)
    return interferenceGraph


# Adds the interferences that exist within a basic block because the previous method only generates the interferences between basic blocks
# Input: the interference graph generated from just using the live ins and live outs of each block
# Output: the complete interference graph, including the inter-block and intra-block interferences
def addSingleBlockInterferences(interferenceGraph, blocks):
    # find the live ins and outs per insn and do the n^2 loop for that
    for block in blocks:
        lives = block.liveOuts
        for insn in reversed(block.insns):
            for i in range(len(insn.defs)):
                curdef = insn.defs[i]
                if (curdef >= 105):
                    curdef = curdef - 101 # save room for r0-r3, r105 starts at index 4 (position 5)
                if (lives[curdef] == 1):
                    lives[curdef] = 0
            for i in range(len(insn.uses)):
                curuse = insn.uses[i]
                if (curuse >= 105):
                    curuse = curuse - 101  # save room for r0-r3, r105 starts at index 4 (position 5)
                if (lives[curuse] == 0):
                    lives[curuse] = 1
            for i in range(len(lives)):
                for j in range(i + 1, len(lives)):
                    if (lives[i] == 1 and lives[j] == 1):
                        interferenceGraph[i][j] = 1
                        interferenceGraph[j][i] = 1
    return interferenceGraph
