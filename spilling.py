# CPE 431: Milestone 3
# John Luu

import controlFlowGraph

# Spill a register
# Input: the control flow graph that represents the RTL
# Output: the control flow graph that is updated with the spilled registers
def spill(cfg):

    # get values from the cfg to use/check
    spillTable = cfg.spillTable
    spilledList = cfg.spilledList
    spilledToList = []

    # determine register to spill
    registerToSpill = -1
    for i in range(105, 105 + cfg.originalNumVirtRegs):
        if (i not in spilledList):
            registerToSpill = i
            spilledList.append(registerToSpill)
            break

    # if out of registers to spill
    if (registerToSpill == -1):
        print("Current Spill Table")
        for key in spillTable.keys():
            print("Key: {} Value: {}".format(key, spillTable[key]))
        print("Error: Spilled all possible registers, not possible with current amount of colors allowed.")
        exit()

    # determine the new register to spill to
    newSpillReg = cfg.numVirtRegs + 105

    # substitute all the appearances of the register that you want to spill with the register that you want to spill to
    for block in cfg.blocks:
        k = 0
        while k < len(block.insns):
            insn = block.insns[k]
            replaced = False

            # go through defs and check if need to substitute
            for i in range(len(insn.defs)):
                if (insn.defs[i] == registerToSpill):
                    insn.defs[i] = newSpillReg
                    replaced = True

            # go through uses and check if need to substitute
            for i in range(len(insn.uses)):
                if (insn.uses[i] == registerToSpill):
                    insn.uses[i] = newSpillReg
                    replaced = True
                    # insert the "store instruction" as the definition
                    newSpillRegList = []
                    newSpillRegList.append(newSpillReg)
                    newLoadInsn = controlFlowGraph.Insn(newSpillRegList, [])
                    block.insns.insert(k, newLoadInsn)

            # if anything was replaced, update the spilled to list, and move the register number to the next available one
            if (replaced):
                spilledToList.append(newSpillReg)
                newSpillReg += 1
            k += 1

    # register doesn't spill to anything bc not being used
    if (len(spilledToList) == 0):
        cfg.spilledList = spilledList
        return spill(cfg)

    # update the spill table
    spillTable[registerToSpill] = spilledToList

    # update the fields in the cfg
    cfg.numVirtRegs = cfg.numVirtRegs + len(spilledToList)
    cfg.spillTable = spillTable
    cfg.spilledList = spilledList

    # update the size of the live ins and live outs to account for the new spilled registers
    for block in cfg.blocks:
        block.liveIns = [0] * (cfg.numVirtRegs + 4)
        block.liveOuts = [0] * (cfg.numVirtRegs + 4)

    return cfg