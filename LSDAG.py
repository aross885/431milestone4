class LSDAG:
    def __init__(self):
        self.insns = []
        self.edges = []

    def __init__(self, insns, edges):
        self.insns = insns
        self.edges = edges



class LSINSN:
    def __init__(self):
        self.defs = []
        self.uses = []
        
    def __init__(self, defs, uses):
        self.defs = defs
        self.uses = uses 