# Programming Languages 2
# Milestone 1

from graphviz import Digraph
from collections import OrderedDict
import sys
import sexpParser

class CFG:
    def __init__(self):
        self.entry = None
        self.exit = None
        self.edgeList = None

    def __init__(self, entry, exit, edgeList):
        self.entry = entry
        self.exit = exit
        self.edgeList = edgeList


class InsnType(enumerate):
    call = 0
    setMem = 1
    use = 2

class Insn:
    def __init__(self):
        self.insnType = None
        self.text = None
        self.next = None
        self.previous = None

class Visited(enumerate):
    notVisited = 0
    visiting = 1
    visited = 2

class Vertex:
    def __init__(self):
        self.insn = None
        self.inEdges = []
        self.outEdges = []
        self.vertNum = None
        self.visited = False

class EdgeType(enumerate):
    BB = 0
    SEQ = 1
    JUM = 2

class Edge:
    def __init__(self):
        self.start = None
        self.end = None
        self.edgetype = None

def parse(rtl, nodes, edges):
    #Parsing the File
    myfile = open(rtl,'r')
    myrtl = myfile.read()
    myrtl = "(" + myrtl + ")"
    test = sexpParser.parse_sexp(myrtl)

    dotfiletext = "{"

    # for jump and seq code labels
    prevBB = 0
    curBB = 0

    labelBBDict = OrderedDict()
    jumpDict = OrderedDict()

    curCodeLabel = -1
    prevInsnType = None
    unlinkedRelationship = False

    lineCount = 0
    for line in test:
        if (lineCount == 2):
            funcName = line
        lineCount += 1
        if type(line) == list:
            if line[0] == 'note':
                if (line[-1] == 'NOTE_INSN_BASIC_BLOCK'):
                    if (curBB == 0):
                        edges.append(('bb_0', 'bb_' + str(line[4])))
                    elif (curBB != 0 and prevInsnType != 'label'):
                        dotfiletext += "}"
                        addToDict(nodes, curBB, dotfiletext)
                        dotfiletext = "{"
                    curBB = line[4]
                    if (prevInsnType == 'label'):
                        addToDict(labelBBDict, curCodeLabel, 'bb_' + str(curBB))
                    if (unlinkedRelationship):
                        edges.append(('bb_' + str(prevBB), 'bb_' + str(curBB)))
                        unlinkedRelationship = False
                    if (dotfiletext != "" and prevInsnType == 'label'):
                        dotfiletext += "|"
                    dotfiletext += str(line[1]) + ": " + str(line[-1]) + "\\ " + str(line[4]) + "\l\\\n"
                elif (line[-1] == 'NOTE_INSN_DELETED'):
                    continue
                else:
                    dotfiletext += "|" + str(line[1]) + ": " + str(line[len(line) - 1]) + "\l\\\n"
                prevInsnType = 'note'

            elif line[0] == 'insn':
                operation = line[5][0]
                if (operation == "set"):
                    if ("mem" in line[5][1][0]):
                        op = line[5][1][1][0]
                        if ("plus" not in op):
                            dst = "mem[" + str(op + " " + str(line[5][1][1][1])) + "]"
                        else:
                            factor = str(line[5][1][1][2][1])
                            dst = "mem[" + str(line[5][1][1][1][0] + " " + str(line[5][1][1][1][1]) + " " + str(factor)) + "]"
                    else:
                        dst = str(line[5][1][0] + " " + str(line[5][1][1]))
                    valueType = str(line[5][2][0])
                    if (valueType == "const_int"):
                        src = str(line[5][2][1])
                    elif ("reg" in valueType):
                        src = str(line[5][2][0] + " " + str(line[5][2][1]))
                    elif ("mem" in valueType):
                        # print(line)
                        # print(line[5][2][1])
                        memAccessType = line[5][2][1]
                        if ("reg" in memAccessType[0]):
                            src = "mem[" + memAccessType[0] + " " + str(memAccessType[1]) + "]"
                        else:
                            factor2 = line[5][2][1][2][1]
                            if ("const_int" not in line[5][2][1][2][0]):
                                factor2 = "symbol_ref"
                            src = "mem[" + str(line[5][2][1][1][0] + " " + str(line[5][2][1][1][1]) + " " + str(factor2)) + "]"
                    elif ("plus" in valueType):
                        # print(line)
                        # print(line[5][2][1][0])
                        addedValueType = str(line[5][2][2][0])
                        # print(addedValueType)
                        src = "plus: use " + str(line[5][2][1][0] + " " + str(line[5][2][1][1])) + " use "
                        if ("reg" in addedValueType):
                            src += str(line[5][2][2][0] + " " + str(line[5][2][2][1]))
                        elif ("const" in addedValueType):
                            src += str(line[5][2][2][1])
                        else:
                            src += str(line[5][2][2][0] + " " + str(line[5][2][2][1]))
                    else:
                        try:
                            if ("symbol_ref" in line[9][1][0]):
                                src = "symbol_ref"
                        except:
                            src = valueType
                    try:
                        if ("symbol_ref" in line[9][1][0] and src != "symbol_ref"):
                            src += " symbol_ref"
                    except:
                        src += ""
                    dotfiletext += "|" + str(line[1]) + ": " + dst + " = " + src + "\l\\\n"
                elif(operation == "use"):
                    srcRegister = str(line[5][1][0] + " " + str(line[5][1][1]))
                    dotfiletext += "|" + str(line[1]) + ": use " + srcRegister + "\l\\\n"
                else:
                    dotfiletext += "|" + str(line[1]) + ": " + operation + "\l\\\n"
                prevInsnType = 'insn'

            elif line[0] == 'call_insn':
                operation = line[5][2][0]
                if (operation == "set"):
                    register = str(line[5][2][1][0] + " " + str(line[5][2][1][1]))
                    function = line[5][2][2][1][1][1][0]
                    dotfiletext += "|" + str(line[1]) + ": " + register + " = call: " + function + "\l\\\n"
                elif (operation == "call"):
                    try:
                        function = line[5][1][1][1][0]
                    except:
                        function = "function_name"
                    dotfiletext += "|" + str(line[1]) + ": call: " + function + "\l\\\n"
                else:
                    dotfiletext += "|" + str(line[1]) + ": call: unknown" + "\l\\\n"
                prevInsnType = 'call'

            elif line[0] == 'jump_insn':
                # case 1: unconditional jump
                if (line[5][2][0] == 'label_ref'):
                    addToDict(jumpDict, 'bb_' + str(curBB), line[5][2][1])
                    dotfiletext += "|" + str(line[1]) + ": jump: pc = L" + str(line[5][2][1])
                # case 2: conditional jump, could be jump or seq
                elif (line[5][2][0] == 'if_then_else'):
                    addToDict(jumpDict, 'bb_' + str(curBB), line[len(line) - 1])
                    prevBB = curBB
                    unlinkedRelationship = True
                    dotfiletext += "|" + str(line[1]) + ": conditional jump: pc = L" + str(line[5][2][2][1])
                prevInsnType = 'jump'

            elif line[0] == 'code_label':
                # case 1: if previous instruction isn't a jump
                if (prevInsnType == 'insn' or prevInsnType == 'call'):
                    prevBB = curBB
                    unlinkedRelationship = True
                dotfiletext += "}"
                addToDict(nodes, curBB, dotfiletext)
                dotfiletext = "{" + (str(line[1]) + ": L" + str(line[1]) + ":\l\\\n")
                curCodeLabel = line[1]
                prevInsnType = 'label'
    dotfiletext += "}"
    addToDict(nodes, curBB, dotfiletext)
    for (k, v) in jumpDict.items():
        edges.append((k, labelBBDict[v]))
    edges.append(('bb_' + str(curBB), 'bb_1'))
    return funcName


def addNode(graph, bbNum, label):
    nodeName = 'bb_' + str(bbNum)
    graph.node(nodeName, label, shape='record', style='filled', fillcolor='lightgrey')

def addEdge(graph, fromName, toName):
    graph.edge(fromName, toName, None, constraint='true')

def addSubgraph(graph, subgraphName, funcName, nodes, edges):
    subgraph = Digraph(name=subgraphName)
    subgraph.attr(style='dashed')
    subgraph.attr(color='black')
    subgraph.attr(label=funcName)

    # entry node
    subgraph.node(
        'bb_0', 'ENTRY', style='filled', shape='Mdiamond', fillcolor='white')

    # middle nodes
    for (k, v) in nodes.items():
        addNode(subgraph, k, v)

    # exit nodes
    subgraph.node(
        'bb_1', 'EXIT', style='filled', shape='Mdiamond', fillcolor='white')

    # add edges
    for (k, v) in edges:
        addEdge(subgraph, k, v)

    # add subgraph to digraph
    graph.subgraph(subgraph)

def addToDict(dict, key, value):
    dict[key] = value

def main():
    if (len(sys.argv) != 2):
        sys.stderr.write("Usage: python rtlParser.py <filename>\n")
        exit(1)

    outputFileName = sys.argv[1]
    dot = Digraph(name = outputFileName)
    dot.attr(overlap = 'false')

    # dictionary of nodes: basic block number -> label
    nodesDict = OrderedDict()

    # dictionary of edges: label1 -> label2
    edgesDict = list()

    # parse input file
    funcName = parse(sys.argv[1], nodesDict, edgesDict)

    # add subgraph for main function
    addSubgraph(dot, 'cluster_' + funcName, funcName + ' ()', nodesDict, edgesDict)

    # output .dot file
    print(dot.source)
    dot.save('my_' + sys.argv[1] + '.dot')


if __name__ == '__main__':
    main()