class CFG:
    def __init__(self):
        self.blocks = []
        self.edges = []
        self.numVirtRegs = 0
        self.originalNumVirtRegs = 0
        self.spillTable = {}
        self.spilledList = []

    def __init__(self, numVirtRegs):
        self.blocks = []
        self.edges = []
        self.numVirtRegs = numVirtRegs
        self.originalNumVirtRegs = numVirtRegs
        self.spillTable = {}
        self.spilledList = []

    def __init__(self, blocks, edges, numVirtRegs):
        self.blocks = blocks
        self.edges = edges
        self.numVirtRegs = numVirtRegs
        self.originalNumVirtRegs = numVirtRegs
        self.spillTable = {}
        self.spilledList = []

class Insn:
    def __init__(self):
        self.defs = []
        self.uses = []

    def __init__(self, defs, uses):
        self.defs = defs
        self.uses = uses


class BasicBlock:
    def __init__(self):
        self.bbnum = None
        self.defs = []
        self.uses = []
        self.neighbors = []
        self.insns = []
        self.liveIns = []
        self.liveOuts = []

    def __init__(self, numVirtRegs):
        self.bbnum = None
        self.defs = []
        self.uses = []
        self.neighbors = []
        self.insns = []
        self.liveIns = [0] * (numVirtRegs + 4)
        self.liveOuts = [0] * (numVirtRegs + 4)

    def __init__(self, bbnum, defs, uses, neighbors, insns, numVirtRegs):
        self.bbnum = bbnum
        self.defs = defs
        self.uses = uses
        self.neighbors = neighbors
        self.insns = insns
        self.liveIns = [0] * (numVirtRegs + 4)
        self.liveOuts = [0] * (numVirtRegs + 4)

# class CFG:
#     def __init__(self, numVirtRegs):
#         self.blocks = []
#         self.edges = []
#         self.numVirtRegs = numVirtRegs
#         self.originalNumVirtRegs = numVirtRegs
#         self.spillTable = {}
#         self.spilledList = []

# class BasicBlock:
#     def __init__(self, numVirtRegs):
#         self.insns = []
#         self.liveIns = [0] * (numVirtRegs + 4)
#         self.liveOuts = [0] * (numVirtRegs + 4)

# class Insn:
#     def __init__(self, defs, uses):
#         self.defs = defs
#         self.uses = uses