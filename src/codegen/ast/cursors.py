from clang.cindex import *

BINARY_ARITHMETIC_OPERATORS = ("+", "-", "*", "/", "%")
UNARY_ARITHMETIC_OPERATORS = ("++", "--")
BINARY_RELATIONAL_OPERATORS = ("==", "!=", ">", "<", ">=", "<=")
BINARY_RELATIONAL_OPERATORS_MT = (">", ">=")
BINARY_RELATIONAL_OPERATORS_LT = ("<", "<=")
BINARY_LOGICAL_OPERATORS = ("&&", "||")


class DopingCursor(Cursor):
    '''
    Doping Cursor which inherits from Clang Cursors and extends it.
    '''

    # IMPORTANT: All Cursor movements/traversals/references should
    # call the instantiate_node to remain inside Doping functionality
    # at the moment the traversal methods implemented are:
    #  -  get_children()
    _parent = None

    @staticmethod
    def _instantiate_node(node):
        if(node.kind == CursorKind.FOR_STMT):
            node.__class__ = ForCursor
            return node
        elif(node.kind == CursorKind.DECL_STMT):
            node.__class__ = DeclarationCursor
            return node
        elif(node.kind == CursorKind.BINARY_OPERATOR):
            node.__class__ = BinaryOperatorCursor
            return node
        else:
            node.__class__ = DopingCursor
            return node

    def get_children(self):
        '''
        Calls Clang AST get_children method but it then instantiate
        the object to proper Doping Cursor subclass.
        '''
        # Retrofit the parent information into the child
        #children_list = []
        #for child in super(DopingCursor, self).get_children():
        #    DopingCursor._instantiate_node(child)
        #    child._parent = self
        #    children_list.append(child)
        #return children_list

        return [DopingCursor._instantiate_node(x)
                for x in super(DopingCursor, self).get_children()]

    def find_file_includes(self):
        # return filter(self.is_from_file, self.root.find_includes())
        # Clang implementation above does not work! FIX! Meanwhile ugly
        # implementation below.
        includes = []
        with open(str(self.location.file), 'r') as f:
            for line in f:
                if line.startswith("#include"):
                    includes.append(line)

        return includes

    ############################
    # HELPER METHODS
    ############################

    # TODO: some should be attributes ??
    def is_for(self):
        return self.kind == CursorKind.FOR_STMT

    def is_compound(self):
        return self.kind == CursorKind.COMPOUND_STMT

    def type_is_scalar(self):
        return ((self.type.kind.value >= 4) and
                (self.type.kind.value <= 23))

    def type_is_pointer(self):
        return (self.type.kind == TypeKind.POINTER)

    def get_start(self):
        return self.extent.start.line

    def get_end(self):
        return self.extent.end.line

    def get_string(self):
        return " ".join([x.spelling for x in self.get_tokens()])

    def contains_str(self, string):
        return string in self.get_string()

    def str_position(self):
        name = str(self.location)
        line = str(self.location.line)
        col = str(self.location.column)
        return "[" + name + ", line:" + line + ", col:" + col + "]"

    ############################
    # PRINTING METHODS
    ############################

    def view(self, indent=0, infile=False, recursion_limit=10):
        '''
        Writes in stdout a representation of the AST tree starting
        at the node.
        '''
        if indent < recursion_limit:
            indentstring = (("| " * indent) + "|-")[2:]
            kind = str(self.kind)[str(self.kind).index('.')+1:]
            text = self.spelling  # or self.displayname
            # Displayname has more information in some situations
            # tokens = " ".join([x.spelling for x in self.get_tokens()])

            print(indentstring + kind + " " + text)
            for child in self.get_children():
                child.view(indent+1)

    def __str__(self):
        result = str(self.kind)[str(self.kind).index('.')+1:]
        if len(self.get_children()) > 0:
            result += "("
            result += ",".join([str(child)
                                for child in self.get_children()])
            result += ")"
        return result

    #######################################
    # find_* Generators
    #######################################

    def find_loops(self, outermostonly=False, exclude_headers=True):
        return self._find(CursorKind.FOR_STMT, outermostonly, exclude_headers)

    def find_includes(self, outermostonly=False, exclude_headers=True):
        return self._find(CursorKind.INCLUSION_DIRECTIVE, True)

    def find_declarations(self, outermostonly=False, exclude_headers=True):
        return self._find(CursorKind.VAR_DECL)

    def find_functions(self, outermostonly=False, exclude_headers=True):
        return self._find(CursorKind.FUNCTION_DECL, exclude_headers)

    def find_assignments(self, outermostonly=False, exclude_headers=True):
        assignments = []
        caos = self._find(CursorKind.COMPOUND_ASSIGNMENT_OPERATOR)
        assignments.extend(caos)

        # Binary operations with '=' operator
        bops = list(self._find(CursorKind.BINARY_OPERATOR))
        assignments.extend(filter(lambda x: x.operator() == "=", bops))

        # Declarations which contain a '='.
        # FIXME: This can have false positives ?
        decls = self._find(CursorKind.DECL_STMT)
        assignments.extend(filter(lambda x: x.contains_str("="), list(decls)))

        return assignments

    def find_array_accesses(self, outermostonly=False,
                            exclude_headers=True):
        return self._find(CursorKind.ARRAY_SUBSCRIPT_EXPR)

    def find_all_accesses(self, outermostonly=False, exclude_headers=True):
        return self._find(CursorKind.UNEXPOSED_EXPR)

    def _find(self, searchtype, outermostonly=False, exclude_headers=True):
        if exclude_headers:
            if self.location.file is not None:
                if self.location.file.name.endswith(('.h', '.hpp', '.tcc')):
                    return  # Does not yield anything
        if (self.kind == searchtype):
            yield self

        # If it needs to continue searching recurse down into the children
        if (self.kind != searchtype or not outermostonly):
            if (self.kind == CursorKind.CALL_EXPR):
                # [1:] to Remove name node of function calls
                for c in self.get_children()[1:]:
                    for match in c._find(searchtype, outermostonly):
                        yield match
            else:
                for c in self.get_children():
                    for match in c._find(searchtype, outermostonly):
                        yield match

    #######################################
    # Analysis methods
    #######################################

    def function_call_analysis(self):

        # Search all function calls in code block
        fcalls = list(self._find(CursorKind.CALL_EXPR))

        # Filter functions not defined in the same file
        # (definition not accessible) (is this enough?)
        # fcalls = [x for x in fcalls if x.get_definition() is not None]

        return fcalls


class BinaryOperatorCursor (DopingCursor):
    '''
    Subclass for AST nodes that containt a BinaryOperator.
    '''
    def operator(self):
        lhs_len = len([x for x in self.get_children()[0].get_tokens()])
        tokens = [x.spelling for x in self.get_tokens()]
        # No Operator or RHS found
        if lhs_len >= len(tokens):
            return None
        return tokens[lhs_len]

class DeclarationCursor (DopingCursor):
    '''
    Subclass for AST nodes that containt a Declaration Statement.

    Declaration statements can be:
    [modifiers] type id;
    [modifiers] type id = value;
    '''
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


class ForCursor (DopingCursor):
    '''
    Subclass for AST nodes that containt a For Loop block.

    For loops have the form:
    for(initialization;end_condition;increment){body}

    FIXME: This is to restrictive, there are more For loop syntaxes now.
    '''

    # Should this be Attributes?
    def get_initialization(self):
        return self.get_children()[0]

    def get_end_condition(self):
        return self.get_children()[1]

    def get_increment(self):
        return self.get_children()[2]

    def get_body(self):
        return self.get_children()[3]

    def initialization_string(self):
        init = self.get_initialization()
        # BUG: libclang get_tokens returns one more token than needed
        tokens = [x.spelling for x in init.get_tokens() if x.spelling != ";"]
        return " ".join(tokens)

    def end_condition_string(self):
        cond = self.get_end_condition()
        tokens = [x.spelling for x in cond.get_tokens() if x.spelling != ";"]
        return " ".join(tokens)

    def increment_string(self):
        incr = self.get_increment()
        tokens = [x.spelling for x in incr.get_tokens()]
        return " ".join(tokens)

    def body_string(self, referencing_variables=None):
        """Return the body of the loop with an appropriate format.

        If a referencing variables is given, any token that matches that
        variable will be prefixed with the C referencing operator * and
        wrapped with paranthesis to maintain operator precedende.
        e.g. "j++;" -> "(*j)++;"
        """

        body = self.get_body()
        string = ""
        line = self.location.line
        after_punctuation = False

        # We need to join the tokens using ' ' and '\n' appropriately.
        for token in body.get_tokens():
            while token.location.line > line:
                for _ in range(line, token.location.line):
                    string = string + "\n"
                line = token.location.line
            # If a list of referencing variables is given and this token
            # matches one of them, add the * prefix.
            if referencing_variables and \
                token.spelling in referencing_variables:
                string += " (*" + token.spelling + ")"
            else:
                if token.kind.name == "PUNCTUATION":
                    # We make a temporary flag to not affect next condition
                    next_after_punctuation = True
                elif after_punctuation:
                    next_after_punctuation = False
                else:
                    next_after_punctuation = False
                    string += " "
                after_punctuation = next_after_punctuation

                string += token.spelling

        # If it is a single statement for (no enclosing '}') it needs a ';'
        if string[-1] != "}":
            string = string + ";"

        return string

    def cond_variable(self):
        tokens = [x.spelling for x in self.get_initialization().get_tokens()]
        if tokens.count(",") > 1:
            raise NotImplementedError(
                "Multiple initialization for loops not implemented yet."
            )
        if tokens.count("=") == 1:
            eqindex = tokens.index("=")
            return tokens[eqindex - 1]
        raise NotImplementedError(
            "Just implemented for loops with simple initialization.")

    def cond_starting_value(self):
        tokens = [x.spelling for x in self.get_initialization().get_tokens()]

        if tokens.count("=") == 1:
            eqindex = tokens.index("=")
            return tokens[eqindex + 1]
        else:
            raise NotImplementedError(
                "Just implemented for loops with simple initialization"
            )

    def cond_variable_type(self):
        """Should return if the loop iterates an int or an unsigned"""

        # Extremely basic version for now, it just hopes it is inline declared
        # and without any typedef or other alias
        # There is more "unsigned" that we don't capture and long types, ...
        # but for now returning int is relatively safe
        tokens = [x.spelling for x in self.get_initialization().get_tokens()]
        if tokens[0] == "unsigned":
            return "unsigned"
        return "int"

    def cond_end_value(self):

        # FIXME: Probably it just work with possitive numbers
        tokens = [x.spelling for x in self.get_end_condition().get_tokens()]

        try:
            endindex = tokens.index(";")
        except ValueError:
            endindex = len(tokens)
        addition = ""

        if tokens.count(",") == 1:
            raise NotImplementedError(
                "Multiple increments for loops not implemented yet."
            )
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
            raise NotImplementedError(
                "Just implemented for loops with simple conditions"
            )

        return ("(" + " ".join(tokens[startindex + 1: endindex]) +
                addition + ")")

    def get_first_n_cond_tokens(self, n=16):

        # Wrong implementation
        tokens = self.get_tokens(self.condition)
        # print(len(tokens))
        if len(tokens) != 4:
            raise NotImplementedError(
                "Just implemented for simple conditions"
            )
        if tokens[1] in BINARY_RELATIONAL_OPERATORS_MT:
            tokens.insert(3, "+")
            tokens.insert(4, "(")
            return tokens
        elif tokens[1] in BINARY_RELATIONAL_OPERATORS_LT:
            tokens.insert(3, "-")
            tokens.insert(4, "(")
            return tokens
        else:
            raise NotImplementedError("Token " + tokens[1] + " not recognized")

    def is_affine(self):
        pass
        # 1) All loop upper bounds and contained control conditions have to
        # be expressible as a linear affine expression in the containing
        # loop index variables and formal parameters (i.e., loop invariant
        # values like function parameters, globals, and so on)
        # 2) Memory accesses can be represented as accesses to a base
        # address (say, the address of an array) at an offset which in turn
        # is an affine function in the loop iteration variables and formal
        # parameters.
        # 2.1) There is no possible aliasing (e.g.,overlap of two arrays)
        # between statically distinct base addresses.
        # 3) There are no calls contained in the loop whose memory effects
        # are statically unknown or which possibly have any observable
        # side-effects or do not provably return.

    def has_multiple_conditions():
        # Last token from the first children of the condition contains
        # the operation
        operator = self.condition.get_children()[0].get_tokens()[-1]
        # .decode("utf-8")
        return not (operator in BINARY_RELATIONAL_OPERATORS)

    def variable_analysis(self):
        '''
        For each variable inside the loop body differenciate between:

        1. Local variables: Variables declared and used only in the loop scope.

        2. Modified global variables: Variables with global scope modified
        within the loop.

        3. Arrays/Pointers readed.

        4. Run-time constants: Variables with global scope but not modified
        in the loop.

        '''
        local_vars = []
        local_vars_names = []
        pointer_vars = []
        pointer_vars_names = []
        written_scalars = []
        written_scalars_names = []
        runtime_constants = []

        # 1. Find local variables: Declared inside the loop.
        for decl in self.find_declarations():
            local_vars.append(decl)
            local_vars_names.append(decl.displayname)

        # 2. Find variables that are written in the loop.
        for assignment in self.find_assignments():
            var = assignment.get_children()[0]
            # If it has pointer operations ignore them until the variable
            # name is found. FIXME: Is this robust enough?
            while var.kind == CursorKind.MEMBER_REF_EXPR:
                var = var.get_children()[0]
            while var.kind == CursorKind.UNARY_OPERATOR:
                var = var.get_children()[0]
            if var.type_is_pointer():
                continue
            if (var.displayname not in local_vars_names) and \
               (var.displayname not in written_scalars_names):
                # avoid duplicated (FIXME: but what happens with
                # multiple declarations with same name?)
                if var.kind != CursorKind.ARRAY_SUBSCRIPT_EXPR:
                    written_scalars.append(var)
                    written_scalars_names.append(var.displayname)

        # 3. Find arrays read in the loop (raw pointers are added in the
        # loop below).
        for array in self.find_array_accesses():
            while array.get_children()[0].displayname == "":
                # recurse down in case it is a multidimensional array
                array = array.get_children()[0]
            # avoid duplicates
            if array.get_children()[0].displayname not in pointer_vars_names:
                pointer_vars.append(array.get_children()[0])
                pointer_vars_names.append(array.get_children()[0].displayname)

        # 4. Variables which can be constant between loop iterations
        runtime_constants = []
        runtime_constants_names = []
        for access in self.find_all_accesses():
            # if access.displayname == "mid":
            #     import pdb; pdb.set_trace()
            #     print(access.type.spelling)
            if access.displayname == "hit":
                import pdb; pdb.set_trace()
            if access.displayname.startswith("operator"):
                continue
            while len(access.get_children()) > 0 and access.kind == CursorKind.UNEXPOSED_EXPR:
                if access.get_children()[0].displayname == access.displayname:
                    access = access.get_children()[0]
                else:
                    break
            while access.kind == CursorKind.MEMBER_REF_EXPR:
                access = access.get_children()[0]
            if (access.displayname not in runtime_constants_names) and \
               (access.displayname not in local_vars_names) and \
               (access.displayname not in written_scalars_names) and \
               (access.displayname not in pointer_vars_names) and \
               (access.displayname != ''):
                if access.type_is_scalar() and \
                   (access.kind != CursorKind.CALL_EXPR):
                    runtime_constants.append(access)
                    runtime_constants_names.append(access.displayname)
                if access.type_is_pointer() and \
                   (access.kind != CursorKind.CALL_EXPR):
                    pointer_vars.append(access)
                    pointer_vars_names.append(access.displayname)

        return local_vars, pointer_vars, written_scalars, runtime_constants