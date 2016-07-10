import sys
import os.path
import clang.cindex

BINARY_ARITHMETIC_OPERATORS = ("+","-","*","/","%")
UNARY_ARITHMETIC_OPERATORS = ("++","--")

BINARY_RELATIONAL_OPERATORS = ("==","!=",">","<",">=","<=")
BINARY_RELATIONAL_OPERATORS_MT = (">",">=")
BINARY_RELATIONAL_OPERATORS_LT = ("<","<=")
BINARY_LOGICAL_OPERATORS = ("&&","||")

class ASTNode:
    
    root = None # is this equivalent to cursor from parent?
    filename = None

    def __init__(self, filename, node = None): 

        if isinstance(node, clang.cindex.Cursor):
            # Instantiate new node
            self.filename = filename
            self.root = node
        else: # if no node is given, parse the filename
            if not os.path.isfile(filename):
                raise ValueError("ASTNode must be initialized with a node or a filename")
            extension = os.path.splitext(filename)[1]
            if extension not in (".c",".cc",".cpp"):
                raise ValueError("Unrecognized file extension (needed by LibClang): " + filename)

            index = clang.cindex.Index.create()
            tu = index.parse(filename)
            self.root = tu.cursor
            self.filename = filename

    def isFor(self):
        return self.root.kind == clang.cindex.CursorKind.FOR_STMT

    def isCompound(self):
        return self.root.kind == clang.cindex.CursorKind.COMPOUND_STMT

    def get_start(self):
        return self.root.extent.start.line

    def get_end(self):
        return self.root.extent.end.line


    def get_tokens(self): # FIXME: Move to parent
        return [x.spelling.decode("utf-8") for x in self.root.get_tokens()]

    def _is_from_file(self, node):
        return node.location.file.name.decode("utf-8") == self.filename
    
    def str_position(self):
        name = self.root.location.file.name.decode("utf-8") 
        line = str(self.root.location.line)
        col  = str(self.root.location.column) 
        return "["+ name + ", line:" + line + ", col:" + col+ "]"

    def node_to_str(self, node, recursion_level = 0):
            childrenstr = []
            if recursion_level < 5:
                for child in filter(self._is_from_file,node.get_children()) :
                    childrenstr.append(self.node_to_str(child,recursion_level+1))
            # Displayname has more information in some situations
            text = node.spelling or node.displayname
            kind = str(node.kind)[str(node.kind).index('.')+1:]
            tokens = [x.spelling for x in node.get_tokens()]
            return  ("   " * recursion_level) + kind + " " + text.decode("utf-8") + "\n" + "\n".join(childrenstr)

    def find_loops(self, fromfile = False):
        looplist = self._find(self.root, clang.cindex.CursorKind.FOR_STMT)
        if fromfile == True: looplist = filter(self._is_from_file, looplist)
        looplist = [ASTNode(self.filename,x) for x in looplist]
        return looplist

    def _find(self, node, type = None):
        listofmatches = []

        try:
            if (node.kind == type): listofmatches.append(node)
        except ValueError:
            pass
         
        # Recurse for children of this node
        for c in node.get_children():
            listofmatches.extend(self._find(c,type))

        return listofmatches

    def get_children(self):
        return [ASTNode(self.filename, x) for x in self.root.get_children()]

    def __str__(self):
        return "AST:\n" + self.node_to_str(self.root)


class FORNode (ASTNode) :
    initialization = None
    condition = None
    increment = None
    body = None

    def __init__(self, node):
        if not node.isFor():
             raise ValueError("when instantiating FOR_AST, node argument must be of kind FOR_STMT")
        self.root = node.root
        child = [ c for c in self.root.get_children()]
        self.initialization = child[0]
        self.condition = child[1]
        self.increment = child[2]
        self.body = child[3]

    def get_init_tokens(self):  
        # Can not call self.get_tokens because there is a bug in libclang and we need [:-1]
        return [x.spelling.decode("utf-8") for x in self.initialization.get_tokens()][:-1]

    def get_cond_tokens(self):
        return [x.spelling.decode("utf-8") for x in self.condition.get_tokens()]

    def get_body(self):
        return ASTNode(self.filename, self.body)

    def cond_variable(self):
        tokens = self.get_init_tokens()
        if tokens.count("=") == 1:
            eqindex = tokens.index("=")
            return tokens[eqindex - 1]
        else:
            raise NotImplementedError("Just implemented for loops with simple initialization")

    def cond_starting_value(self):
        tokens = self.get_init_tokens()
        if tokens.count("=") == 1:
            eqindex = tokens.index("=")
            return tokens[eqindex + 1]
        else:
            raise NotImplementedError("Just implemented for loops with simple initialization")
        pass

    def cond_end_value(self):

        # FIXME: Probably it just work with possitive numbers
        tokens = self.get_cond_tokens()
        endindex = tokens.index(";")
        addition = ""

        if tokens.count("<") == 1:
            startindex = tokens.index("<")
            addition = " - 1"
        elif tokens.count(">") == 1:
            eqindex = tokens.index(">")
            addition = " + 1"
        elif tokens.count("<=") == 1:
            eqindex = tokens.index("<=")
        elif tokens.count(">=") == 1:
            eqindex = tokens.index(">=")
        else:
            raise NotImplementedError("Just implemented for loops with simple conditions")

        return "(" + " ".join(tokens[startindex + 1 : endindex]) + addition + ")"

    

    def get_first_n_cond_tokens(self, n = 16):
        
        # Wrong implementation
        tokens = self.get_tokens(self.condition)
        print(len(tokens))
        if len(tokens) != 4:
            raise NotImplementedError("Just implemented for simple conditions")
        if tokens[1] in BINARY_RELATIONAL_OPERATORS_MT:
            tokens.insert(3,"+")
            tokens.insert(4,"(")
            return tokens
        elif tokens[1] in BINARY_RELATIONAL_OPERATORS_LT:
            tokens.insert(3,"-")
            tokens.insert(4,"(")
            return tokens
        else:
            raise NotImplementedError("Token " + tokens[1] + " not recognized")
    
    def get_incr_tokens(self):
        return [x.spelling.decode("utf-8") for x in self.increment.get_tokens()]

    def get_body_tokens(self):
        return [x.spelling.decode("utf-8") for x in self.body.get_tokens()][:-1]

    def is_affine(self):
        # 1) All loop upper bounds and contained control conditions have to be
        # expressible as a linear affine expression in the containing loop index
        # variables and formal parameters (i.e., loop invariant values like function
        # parameters, globals, and so on)
        # 2) Memory accesses can be represented as accesses to a base address (say,
        # the address of an array) at an offset which in turn is an affine function
        # in the loop iteration variables and formal parameters.
        # 2.1) There is no possible aliasing (e.g.,overlap of two arrays) between 
        # statically distinct base addresses.
        # 3) There are no calls contained in the loop whose memory effects are 
        # statically unknown or which possibly have any observable side-effects
        # or do not provably return.
        pass

    def has_multiple_conditions():
        # Last token from the first children of the condition contains the operation
        operator = self.condition.get_children()[0].get_tokens()[-1].decode("utf-8")
        return not (operator in BINARY_RELATIONAL_OPERATORS) 


