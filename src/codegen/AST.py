import sys
import os.path
import clang.cindex

BINARY_ARITHMETIC_OPERATORS = ("+","-","*","/","%")
UNARY_ARITHMETIC_OPERATORS = ("++","--")

BINARY_RELATIONAL_OPERATORS = ("==","!=",">","<",">=","<=")
BINARY_RELATIONAL_OPERATORS_MT = (">",">=")
BINARY_RELATIONAL_OPERATORS_LT = ("<","<=")
BINARY_LOGICAL_OPERATORS = ("&&","||")


def instantiate_node(node, filename):
    if(node.kind == clang.cindex.CursorKind.FOR_STMT):
        return FORNode(filename, node)
    elif(node.kind == clang.cindex.CursorKind.DECL_STMT):
        return DECLNode(filename, node)
    else:
        return ASTNode(filename, node)


class ASTNode:
    
    node = None # is this equivalent to cursor from parent?
    filename = None

    def __init__(self, filename, other = None): 

        if isinstance(other, clang.cindex.Cursor):
            # Instantiate new node
            self.filename = filename
            self.node = other
        else: # if no node is given, parse the filename
            if not os.path.isfile(filename):
                raise ValueError("ASTNode must be initialized with a node or a filename")
            extension = os.path.splitext(filename)[1]
            if extension not in (".c",".cc",".cpp"):
                raise ValueError("Unrecognized file extension (needed by LibClang): " + filename)

            index = clang.cindex.Index.create()
            tu = index.parse(filename)
            self.node = tu.cursor
            self.filename = filename

    def isFor(self):
        return self.node.kind == clang.cindex.CursorKind.FOR_STMT

    def isCompound(self):
        return self.node.kind == clang.cindex.CursorKind.COMPOUND_STMT

    def get_start(self):
        return self.node.extent.start.line

    def get_end(self):
        return self.node.extent.end.line


    def get_tokens(self): # FIXME: Move to parent
        return [x.spelling.decode("utf-8") for x in self.node.get_tokens()]

    def contains(self, other, string):
        tokens = [x.spelling.decode("utf-8") for x in other.get_tokens()]
        return string in tokens

    def _is_from_file(self, other):
        return other.location.file.name.decode("utf-8") == self.filename
    
    def str_position(self):
        name = self.node.location.file.name.decode("utf-8") 
        line = str(self.node.location.line)
        col  = str(self.node.location.column) 
        return "["+ name + ", line:" + line + ", col:" + col+ "]"

    def node_to_str(self, other, ptokens=True, recursion_level = 0):
        childrenstr = []
        if recursion_level < 5:
            for child in filter(self._is_from_file,other.get_children()) :
                childrenstr.append(self.node_to_str(child,ptokens,recursion_level+1))
        # Displayname has more information in some situations
        text = other.spelling or other.displayname
        kind = str(other.kind)[str(other.kind).index('.')+1:]
        tokens = ""
        if ptokens:
            tokens = " ".join([x.spelling for x in other.get_tokens()])
        return  ("   " * recursion_level) + kind + " " + text.decode("utf-8") + " " + tokens + "\n" + "\n".join(childrenstr)

    def find_loops(self, fromfile = False):
        looplist = self._find(self.node, clang.cindex.CursorKind.FOR_STMT)
        if fromfile == True: looplist = filter(self._is_from_file, looplist)
        looplist = [FORNode(self.filename,x) for x in looplist]
        return looplist

 
    def find_declarations(self, fromfile = False):
        decllist = self._find(self.node, clang.cindex.CursorKind.DECL_STMT)
        if fromfile == True: decllist = filter(self._is_from_file, decllist)
        decllist = [DECLNode(self.filename,x) for x in decllist]
        return decllist

    def find_writes(self, fromfile = False):
        assigments = []
        assigments.extend(self._find(self.node, clang.cindex.CursorKind.COMPOUND_ASSIGNMENT_OPERATOR))
        #print "compound assignments: " + str(len(assigments))

        # Binary operations which contain a '='
        found = self._find(self.node, clang.cindex.CursorKind.BINARY_OPERATOR)
        assigments.extend(filter(lambda x: self.contains(x,"="), list(found)))
        #print "binary ops: " + str(len(found))

        # Declarations which contain a '='
        found = self._find(self.node, clang.cindex.CursorKind.DECL_STMT)
        assigments.extend(filter(lambda x: self.contains(x,"="), list(found)))
        #print "declarations: " + str(len(found))

        if fromfile == True: assigments = filter(self._is_from_file, assigments)    

        writes = []

        for a in assigments:
            if self.contains(a,"="):
                tokens = [x.spelling for x in a.get_tokens()]
                ind = tokens.index('=')
                #if it is not an array
                if tokens[ind-1] != ']':
                    #FIXME: should consider composed references (e.g. structs)
                    writes.append(tokens[ind-1])
            c1 = list(a.get_children())[0]
            if c1.kind == clang.cindex.CursorKind.ARRAY_SUBSCRIPT_EXPR:
                writes.append(list(c1.get_tokens())[0].spelling)

        return writes

    def find_reads(self):

        names = {}
        def _get_names(other, parent):
            text = other.spelling or other.displayname
            if text not in names and not text == "":
                names[text]=parent.kind
            #print(text+" : "+ str(other.kind) + "," +str(parent.kind))
            child = other.get_children()
            for c in child:
                _get_names(c, other)
            return names
    
        reads = _get_names(self.node, self.node)
    
        reads = [x for x in names.keys() if not names[x]==clang.cindex.CursorKind.ARRAY_SUBSCRIPT_EXPR]
        reads_array = [x for x in names.keys() if names[x]==clang.cindex.CursorKind.ARRAY_SUBSCRIPT_EXPR]
        return reads, reads_array
    


    def find_type(self,var):
        #FIXME: Find the type
        #print("Find type of " + str(var))
        all_dec = []
        all_dec.extend(self._find(self.node, clang.cindex.CursorKind.PARM_DECL))
        all_dec.extend(self._find(self.node, clang.cindex.CursorKind.VAR_DECL))
        all_dec = filter(self._is_from_file,all_dec)
        all_dec = filter( lambda x: x.displayname==var ,all_dec)

        if len(all_dec) < 1:
            raise ValueError("Var " + var + " does not exist in the file.")
        # FIXEM: Solve issue below
        if len(all_dec) > 1:
            raise NotImplementedError("Right now it does not support same var names in the same file")
    
        type_tokens = []
        tokens = [x.spelling for x in all_dec[0].get_tokens()]
        #print tokens
        ind = tokens.index(var)

        # before the variable name there is the tyep (FIXME: NOT ALWAYS)
        ind = ind - 1
        while ind >= 0 and tokens[ind] not in [",",";"]:
            type_tokens.insert(0,tokens[ind])
            ind = ind - 1
        
        # after the variable name there may be array information
        ind = tokens.index(var)
        ind = ind + 1
        while tokens[ind] == '[':
            while tokens[ind] != ']':
                type_tokens.append(tokens[ind])
                ind = ind + 1
            type_tokens.append(']')
            ind = ind + 1

        #print(" ".join(type_tokens))
        #exit(0)
        string = " ".join(type_tokens)
        string = string.replace(' [ ','[')
        return string


    def _find(self, other, type = None):
        listofmatches = []

        try:
            if (other.kind == type): listofmatches.append(other)
        except ValueError:
            pass
         
        # Recurse for children of this node
        for c in other.get_children():
            listofmatches.extend(self._find(c,type))

        return listofmatches

    def get_children(self):
        return [instantiate_node(x, self.filename) for x in self.node.get_children()]

    def __str__(self):
        return "AST:\n" + self.node_to_str(self.node)

class DECLNode (ASTNode):
    datatype = None
    varname = None
    array = None

    def __init__(self, filename, other):
        #if not other.isDecl():
        #    raise ValueError("when instantiating FOR_AST, node argument must be of kind FOR_STMT")
        self.node = other
        self.filename = filename
        tokens = [x.spelling for x in self.node.get_tokens()]
        #print(" ".join(tokens)) 

        if tokens.count("=") == 1:
            # Initialization declaration
            index = tokens.index("=") - 1
        elif tokens.count("=") == 0:
            # Declaration without initialization
            index = tokens.index(";") - 1
        else:
            raise ValueError("Unexpected string")
    
        self.varname = tokens[index]
        self.datatype = " ".join(tokens[0:index])
        


class FORNode (ASTNode) :
    initialization = None
    condition = None
    increment = None
    body = None

    def __init__(self, filename, other):
        if not other.kind == clang.cindex.CursorKind.FOR_STMT:
             raise ValueError("when instantiating FOR_AST, node argument must be of kind FOR_STMT")
        self.node = other
        self.filename = filename
        child = [ c for c in self.node.get_children()]
        self.initialization = child[0]
        self.condition = child[1]
        self.increment = child[2]
        self.body = child[3]

    def get_init_tokens(self):  
        # Can not call self.get_tokens because there is a bug in libclang and we need [:-1]
        return [x.spelling for x in self.initialization.get_tokens()][:-1]

    def get_cond_tokens(self):
        return [x.spelling for x in self.condition.get_tokens()]

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


