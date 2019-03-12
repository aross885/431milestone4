import controlFlowGraph
import liveVariableAnalysis
import interferenceGraph
import graphColorizer

def main():
    numVirtRegs = 5
    cfg = controlFlowGraph.CFG(numVirtRegs)
    bb0 = controlFlowGraph.BasicBlock(numVirtRegs)
    bb1 = controlFlowGraph.BasicBlock(numVirtRegs)
    bb2 = controlFlowGraph.BasicBlock(numVirtRegs)
    bb3 = controlFlowGraph.BasicBlock(numVirtRegs)

    # no spill a
    i0 = controlFlowGraph.Insn([106], [105])
    i1 = controlFlowGraph.Insn([105], [])
    bb0.insns.append(i0)
    bb0.insns.append(i1)
    i2 = controlFlowGraph.Insn([], [107])
    i3 = controlFlowGraph.Insn([108], [106, 107])
    i4 = controlFlowGraph.Insn([107], [])
    bb1.insns.append(i2)
    bb1.insns.append(i3)
    bb1.insns.append(i4)
    i5 = controlFlowGraph.Insn([], [109])
    i6 = controlFlowGraph.Insn([108], [109, 106])
    i7 = controlFlowGraph.Insn([109], [])
    bb2.insns.append(i5)
    bb2.insns.append(i6)
    bb2.insns.append(i7)
    i8 = controlFlowGraph.Insn([], [105, 108])
    i9 = controlFlowGraph.Insn([], [105, 108])
    bb3.insns.append(i8)
    bb3.insns.append(i9)

    # spill a
    # i0 = controlFlowGraph.Insn([106], [110])
    # i1 = controlFlowGraph.Insn([110], [])
    # bb0.insns.append(i0)
    # bb0.insns.append(i1)
    # i2 = controlFlowGraph.Insn([], [107])
    # i3 = controlFlowGraph.Insn([108], [106, 107])
    # i4 = controlFlowGraph.Insn([107], [])
    # bb1.insns.append(i2)
    # bb1.insns.append(i3)
    # bb1.insns.append(i4)
    # i5 = controlFlowGraph.Insn([], [109])
    # i6 = controlFlowGraph.Insn([108], [109, 106])
    # i7 = controlFlowGraph.Insn([109], [])
    # bb2.insns.append(i5)
    # bb2.insns.append(i6)
    # bb2.insns.append(i7)
    # i8 = controlFlowGraph.Insn([], [111, 108])
    # i9 = controlFlowGraph.Insn([], [111, 108])
    # i10 = controlFlowGraph.Insn([111], []) # add def when find a use of a spilled register
    # bb3.insns.append(i8)
    # bb3.insns.append(i9)
    # bb3.insns.append(i10)
    cfg.blocks.append(bb0)
    cfg.blocks.append(bb1)
    cfg.blocks.append(bb2)
    cfg.blocks.append(bb3)

    edges = [[0 for x in range(4)] for y in range(4)]
    edges[0][1] = 1
    edges[0][2] = 1
    edges[1][3] = 1
    edges[2][3] = 1
    cfg.edges = edges

    print("STEP 1: Performing Live Variable Analysis...")
    liveVariableAnalysis.livenessAnalysis(cfg)
    print("STEP 2: Building Interference Graph...")
    ig = interferenceGraph.buildInterferenceGraph(cfg)

    print("\nInterference Graph")
    for i in range(len(ig)):
        print(ig[i])

    print("\nSTEP 3: Coloring Graph...")
    colors = graphColorizer.colorGraph(cfg, ig)
    print("\nColors: ")
    print(colors)

if __name__ == "__main__":
    main()