import LSDAG as ls

def construct_LSAM(vertexList):
    adjMat = []
    ind = 0
    for i in range(len(vertexList)):
        adjMat.append([0 for i in range(len(vertexList))])
    for i in range(len(vertexList)):
        if len(vertexList[i].defs) == 0:
            continue
        theDef = vertexList[i].defs[0]
        for j in range(i+1, len(vertexList)):
            if theDef in vertexList[j].uses:
                adjMat[i][j] = 1
    return adjMat


def create_LSDAG(cfg):
    instructions = []
    for block in cfg.blocks:
        for insn in block.insns:
            instructions.append(ls.LSINSN(insn.defs, insn.uses))
    adjMat = construct_LSAM(instructions)
    return ls.LSDAG(instructions, adjMat)
    

