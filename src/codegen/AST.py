import sys
import os.path
import clang.cindex

BINARY_ARITHMETIC_OPERATORS = ("+","-","*","/","%")
UNARY_ARITHMETIC_OPERATORS = ("++","--")
BINARY_RELATIONAL_OPERATORS = ("==","!=",">","<",">=","<=")
BINARY_RELATIONAL_OPERATORS_MT = (">",">=")
BINARY_RELATIONAL_OPERATORS_LT = ("<","<=")
BINARY_LOGICAL_OPERATORS = ("&&","||")


def instantiate_node(node):
    if(node.kind == clang.cindex.CursorKind.FOR_STMT):
        node.__class__ = FORNode
        return node
    elif(node.kind == clang.cindex.CursorKind.DECL_STMT):
        node.__class__ = DECLNode
        return node
    else:
        node.__class__ = ASTNode
        return node


class AST:
    filanme = None
    root = None

    def __init__(self, filename):
        if not os.path.isfile(filename):
            raise ValueError("filename does not exist")
        extension = os.path.splitext(filename)[1]
        if extension not in (".c",".cc",".cpp"):
            raise ValueError("Unrecognized file extension" + \
                    "(needed by LibClang): " + filename)

        index = clang.cindex.Index.create()
        tu = index.parse(filename)
        self.root = tu.cursor
        self.filename = filename
        self.root.__class__ = ASTNode

    def find_file_loops(self, outermostonly=False):
        def is_from_file(node):
            return node.location.file.name.decode("utf-8") == self.filename

        return filter(is_from_file, self.root.find_loops(outermostonly))


    def get_root(self):
        return self.root


class ASTNode(clang.cindex.Cursor):

    def isFor(self):
        return self.kind == clang.cindex.CursorKind.FOR_STMT

    def isCompound(self):
        return self.kind == clang.cindex.CursorKind.COMPOUND_STMT

    def get_start(self):
        return self.extent.start.line

    def get_end(self):
        return self.extent.end.line

    def get_string(self):
        return " ".join([x.spelling for x in self.get_tokens()])

    def contains_str(self, string):
        return string in self.get_string()

    def str_position(self):
        name = self.location.file.name.decode("utf-8") 
        line = str(self.location.line)
        col  = str(self.location.column) 
        return "["+ name + ", line:" + line + ", col:" + col+ "]"

    def node_to_str(self, ptokens=False, recursion_level = 0):
        childrenstr = []
        if recursion_level < 5:
            for child in self.get_children() :
                childrenstr.append(child.node_to_str(ptokens,recursion_level+1))

        # Displayname has more information in some situations
        text = self.spelling or self.displayname
        kind = str(self.kind)[str(self.kind).index('.')+1:]
        tokens = ""
        #tokens = " ".join([x.spelling for x in self.get_tokens()])
        return  ("   " * recursion_level) + kind + " " + text.decode("utf-8") \
                + " " + tokens + "\n" + "\n".join(childrenstr)


    def _find(self, searchtype, outermostonly = False):
        if (self.kind == searchtype):
            yield self

        # If it needs to contimue searching recurse into the children
        if (self.kind != searchtype or not outermostonly):    
            for c in self.get_children():
                for match in c._find(searchtype, outermostonly):
                    yield match


    def find_loops(self, outermostonly = True,):
        return self._find(clang.cindex.CursorKind.FOR_STMT, outermostonly)

    def find_declarations(self):
        return self._find(clang.cindex.CursorKind.DECL_STMT)
        

    def find_assignments(self, fromfile = False):
        assignments = []
        caos = self._find(clang.cindex.CursorKind.COMPOUND_ASSIGNMENT_OPERATOR)
        assignments.extend(caos)

        # Binary operations which contain a '='
        bops = self._find(clang.cindex.CursorKind.BINARY_OPERATOR)
        assignments.extend(filter(lambda x: x.contains_str("="), list(bops)))

        # Declarations which contain a '='
        decls = self._find(clang.cindex.CursorKind.DECL_STMT)
        assignments.extend(filter(lambda x: x.contains_str("="), list(decls)))

        return assignments

    def find_array_accesses(self):
        return self._find(clang.cindex.CursorKind.ARRAY_SUBSCRIPT_EXPR)

    def find_all_accesses(self):
        return self._find(clang.cindex.CursorKind.UNEXPOSED_EXPR)
    def get_children(self):
        return [instantiate_node(x) for x in super(ASTNode,self).get_children()]

    def __str__(self):
        return "AST:\n" + self.node_to_str(self)

class DECLNode (ASTNode):

    def get_type_id_string(self):
        tokens = [x.spelling for x in self.get_tokens()]

        if tokens.count("=") == 1:
            # Initialization declaration
            index = tokens.index("=") - 1
        elif tokens.count("=") == 0:
            # Declaration without initialization
            index = tokens.index(";") - 1
        else:
            raise ValueError("Unexpected string")

        varname = tokens[index]
        datatype = " ".join(tokens[0:index])
        return datatype, varname


class FORNode (ASTNode) :

    def get_init_string(self):  
        init = self.get_children()[0]
        # bug in libclang get_tokens, it returns one more token than needed
        tokens = [x.spelling for x in init.get_tokens()]
        tokens = tokens[:tokens.index(";")]
        return " ".join(tokens)

    def get_init_tokens(self):
        init = self.get_children()[0]
        # bug in libclang get_tokens, it returns one more token than needed
        tokens = [x.spelling for x in init.get_tokens()]
        return tokens[:tokens.index(";")]

    def get_cond_string(self):
        cond = self.get_children()[1]
        tokens = [x.spelling for x in cond.get_tokens()]
        tokens = tokens[:tokens.index(";")]
        return " ".join(tokens)

    def get_cond_tokens(self):
        cond = self.get_children()[1]
        tokens = [x.spelling for x in cond.get_tokens()]
        return tokens[:tokens.index(";")]

    def get_incr_string(self):
        incr = self.get_children()[2]
        return " ".join([x.spelling for x in incr.get_tokens()])

    def get_body_string(self):
        body = self.get_children()[3]
        # bug in libclang get_tokens, it returns one more token than needed
        # [:-1] due to a bug in libclang?
        string = ""
        line = list(body.get_tokens())[0].location.line
        for token in list(body.get_tokens())[:-1]:
            while (token.location.line > line):
                line = line + 1
                string = string + "\n"
            string = string + " " + token.spelling


        # bug in libclang get_tokens, it returns one more token than needed
        string = string + ";"
        return string


    def get_body(self):
        return self.get_children()[3]

    def cond_variable(self):
        init = self.get_children()[0]
        tokens = [x.spelling for x in init.get_tokens()]
        if tokens.count("=") == 1:
            eqindex = tokens.index("=")
            return " ".join(tokens[eqindex - 1])
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

        try:
            endindex = tokens.index(";")
        except:
            endindex = len(tokens)
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


    def is_affine(self):
        pass
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

    def has_multiple_conditions():
        # Last token from the first children of the condition contains the operation
        operator = self.condition.get_children()[0].get_tokens()[-1].decode("utf-8")
        return not (operator in BINARY_RELATIONAL_OPERATORS) 

    def variable_analysis(self):
        """ For each variable inside the loop body differenciate between:
        - Local variables: Variables declared and used only in the loop scope
        - Modified global variables: Variables with global scope modified within the loop
        - Arrays/Pointers readed:
        - Run-time constants: Variables with global scope but not modified in the loop
        """
        local_vars = []
        arrays = []
        written_scalars = []
        runtime_constants = []

        for decl in self.find_declarations():
            local_vars.append(decl.get_children()[0])

        arrays = map(lambda x: x.get_children()[0],self.find_array_accesses())
        arrays_dp = map(lambda x : x.displayname, arrays)
        decl_dp = map(lambda x : x.displayname, local_vars)

        for assignment in self.find_assignments():
            var = assignment.get_children()[0]
            if var not in local_vars: # FIXME: first element
                if var.kind != clang.cindex.CursorKind.ARRAY_SUBSCRIPT_EXPR:
                    written_scalars.append(var)

        write_dp = map(lambda x : x.displayname, written_scalars)
        runtime_constants = []
        ru_dp = []
        for access in self.find_all_accesses():
            if (access.displayname not in ru_dp) and \
               (access.displayname not in decl_dp) and \
               (access.displayname not in arrays_dp) and \
               (access.displayname != ''):
                    ru_dp.append(access.displayname)
                    runtime_constants.append(access)


        print ("Local vars: ")
        for var in local_vars:
            print "  Found "+ var.displayname + " ("+ var.type.spelling + ")"
        print ("Arrays: " )
        for var in arrays:
            v = var.get_children()[0]
            print "  Found "+ v.displayname + " ("+ v.type.spelling + ")"
        print ("Scalar writes: " )
        for var in written_scalars:
            print "  Found "+ var.displayname + " ("+ var.type.spelling + ")"
        print ("Vars for delayed evaluation: " )
        for var in runtime_constants:
            print "  Found "+ var.displayname + " ("+ var.type.spelling + ")"

        return local_vars, arrays, written_scalars, runtime_constants


