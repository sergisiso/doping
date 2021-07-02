""" Extends libclang library functionality by providing cursor sub-classes
of certain node kinds"""

import sys
from clang.cindex import Cursor, CursorKind, TypeKind

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

    # DopingCursors have a reference to its parent on the AST tree
    _parent = None
    _root = None

    # IMPORTANT: All Cursor movements/traversals/references should
    # call the instantiate_node to remain inside Doping functionality
    # at the moment the traversal methods implemented are:
    #  -  get_children()

    @staticmethod
    def _instantiate_node(node):
        if node.kind == CursorKind.FOR_STMT:
            node.__class__ = ForCursor
        elif node.kind == CursorKind.DECL_STMT:
            node.__class__ = DeclarationCursor
        elif node.kind == CursorKind.BINARY_OPERATOR:
            node.__class__ = BinaryOperatorCursor
        elif node.kind == CursorKind.CALL_EXPR:
            node.__class__ = CallCursor
        else:
            node.__class__ = DopingCursor
        return node

    def get_children(self):
        ''' Return the children nodes of this AST node.

        Note: In addition to the libclang functionallity, this method dynamically
        changes the node sub-class to the appropriate Doping sub-class. It also
        retrofits the parent information to the children nodes.
        '''
        # Retrofit the parent information into the children
        children_list = []
        for child in super().get_children():
            DopingCursor._instantiate_node(child)
            # pylint: disable=protected-access
            child._parent = self
            child._root = self.root
            # pylint: enable=protected-access
            children_list.append(child)
        return children_list

    @property
    def root(self):
        ''' Return the root node of the AST '''
        return self._root

    def find_definition(self, exclude_headers=True):
        node = super().get_definition()
        if node is not None:
            if exclude_headers and node.location.file.name != self.location.file.name:
                return None
            DopingCursor._instantiate_node(node)
            # pylint: disable=protected-access
            node._root = self.root
            # pylint: enable=protected-access
            return node
        return None

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
        return ((self.type.kind.value >= 3) and
                (self.type.kind.value <= 23))

    def type_is_pointer(self):
        return (self.type.kind == TypeKind.POINTER)

    def get_start(self):
        return self.extent.start.line

    def get_end(self):
        return self.extent.end.line

    def get_string(self, referencing_variables=None):
        """Return the whole string that this node represents.

        If a referencing variables is given, any token that matches that
        variable will be prefixed with the C referencing operator * and
        wrapped with paranthesis to maintain operator precedende.
        e.g. "j++;" -> "(*j)++;"
        """

        if referencing_variables is None:
            return self.get_string_from_source()
        string = ""
        line = self.location.line

        # Sometimes get_tokens() does not return the expected tokens. This
        # may be a BUG in libclang.
        tokens = self.get_tokens()
        if len(tokens) <= 0:
            print("Probably a get_tokens error! Stopping")
            sys.exit(-1)

        # We need to join the tokens using ' ' and '\n' appropriately.
        for token in tokens:
            while token.location.line > line:
                if string[-1] == " ":
                    string = string[:-1]
                for _ in range(line, token.location.line):
                    string = string + "\n"
                line = token.location.line
            if referencing_variables and token.spelling in referencing_variables:
                # If a list of referencing variables is given and this token
                # matches one of them, add the * prefix.
                string += " (*" + token.spelling + ")"
            elif token.kind.name == "PUNCTUATION":
                # If we have a punctuation token (e.g. struct.element), do not
                # add a whitespace after the token.
                string += token.spelling
            else:
                string += token.spelling + " "

        if len(string) > 0 and string[-1] == " ":
            string = string[:-1]
        return string

    def contains_str(self, key):
        return key in self.get_string()

    def str_position(self):
        name = str(self.location)
        line = str(self.location.line)
        col = str(self.location.column)
        return "[" + name + ", line:" + line + ", col:" + col + "]"

    ############################
    # PRINTING METHODS
    ############################

    def view(self, indent=0, infile=False, recursion_limit=15):
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

    def _find(self, searchtype, outermostonly=False, exclude_headers=True):

        # Search type must be a tuple to allow multiple search types
        if not isinstance(searchtype, tuple):
            searchtype = (searchtype,)

        if exclude_headers:
            if self.location.file is not None:
                if self.location.file.name.endswith(('.h', '.hpp', '.tcc')):
                    return  # Does not yield anything

        # Found a node if searchtype
        if self.kind in searchtype:
            yield self

        # If it needs to continue searching recurse down into the children
        if self.kind not in searchtype or not outermostonly:
            if self.kind == CursorKind.CALL_EXPR:
                # [1:] to Remove name node of function calls
                for child in self.get_children()[1:]:
                    for match in child._find(searchtype, outermostonly):
                        yield match
            else:
                for child in self.get_children():
                    for match in child._find(searchtype, outermostonly):
                        yield match

    def find_loops(self, outermostonly=False, exclude_headers=True):
        ''' Find For Statements nodes '''
        return self._find(CursorKind.FOR_STMT, outermostonly, exclude_headers)

    def find_includes(self, outermostonly=False, exclude_headers=True):
        ''' Find Include Directive nodes '''
        return self._find(CursorKind.INCLUSION_DIRECTIVE, True)

    def find_declarations(self, outermostonly=False, exclude_headers=True):
        ''' Find Variables Declarations nodes '''
        return self._find(CursorKind.VAR_DECL)

    def find_functions(self, outermostonly=False, exclude_headers=True):
        ''' Find Function Declarations nodes '''
        return self._find(CursorKind.FUNCTION_DECL, exclude_headers)

    def find_assignments(self, outermostonly=False, exclude_headers=True):
        ''' Find Assignment nodes '''
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

    def find_array_accesses(self, outermostonly=False, exclude_headers=True):
        ''' Find Array Accesses nodes '''
        return self._find(CursorKind.ARRAY_SUBSCRIPT_EXPR)

    def find_all_accesses(self, outermostonly=False, exclude_headers=True):
        ''' Find Accesses nodes '''
        return self._find((CursorKind.UNEXPOSED_EXPR, CursorKind.DECL_REF_EXPR))

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

    def get_string_from_source(self):
        ''' Get the string representing this node by using the extents
        to cut the original source code. '''

        start = self.extent.start.line - 1  # 1 to 0-indexing
        end = self.extent.end.line - 1  # 1 to 0-indexing
        block = self.root.source_code.split('\n')[start:end + 1]

        col_start = self.extent.start.column - 1  # 1 to 0-indexing
        block[0] = block[0][col_start:]
        col_end = self.extent.end.column - 1  # 1 to 0-indexing
        block[-1] = block[-1][:col_end + 1]

        return '\n'.join(block)


class DopingRootCursor (DopingCursor):
    ''' Special Cursor for the AST Root node '''

    _source_code = None

    @property
    def _root(self):
        return self

    @property
    def source_code(self):
        ''' Return the original source code represented by this AST '''
        return self._source_code


class CallCursor (DopingCursor):
    ''' Subclass for Function call nodes '''

    def get_declaration(self):
        ''' Get the function declaration '''
        definition = self.get_definition()

        if definition:
            return definition
        return None


class BinaryOperatorCursor (DopingCursor):
    '''
    Subclass for AST nodes that containt a BinaryOperator.
    '''
    def operator(self):
        ''' Return the operator token. '''
        lhs_len = len(list(self.get_children()[0].get_tokens()))
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
        ''' Returns a tuple with the type and the id of this declaration. '''
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
        ''' Get For Initialization child node. '''
        return self.get_children()[0]

    def get_end_condition(self):
        ''' Get For Condition child node. '''
        return self.get_children()[1]

    def get_increment(self):
        ''' Get For Increment child node. '''
        return self.get_children()[2]

    def get_body(self):
        ''' Get Initialization child node. '''
        return self.get_children()[3]

    def initialization_string(self):
        ''' Get For Initialization string. '''
        init = self.get_initialization()
        # BUG: libclang get_tokens returns one more token than needed
        tokens = [x.spelling for x in init.get_tokens() if x.spelling != ";"]
        return " ".join(tokens)

    def end_condition_string(self):
        ''' Get For Condition string. '''
        cond = self.get_end_condition()
        tokens = [x.spelling for x in cond.get_tokens() if x.spelling != ";"]
        return " ".join(tokens)

    def increment_string(self):
        ''' Get For Increment string. '''
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

        string = self.get_body().get_string(referencing_variables=referencing_variables)

        # If it is a single statement for (no enclosing '}') it needs a ';'
        if string[-1] != "}":
            string = string + ";"

        return string

    def cond_variable(self):
        ''' Return the variable used in this For Loop as iterator. '''
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
        ''' Return the For iteration starting expression '''
        tokens = [x.spelling for x in self.get_initialization().get_tokens()]

        if tokens.count("=") == 1:
            eqindex = tokens.index("=")
            return tokens[eqindex + 1]
        raise NotImplementedError(
            "Just implemented for loops with simple initialization"
        )

    def cond_variable_type(self):
        """Return if the loop iterates an int or an unsigned. """

        # Extremely basic version for now, it just hopes it is inline declared
        # and without any typedef or other alias
        # There is more "unsigned" that we don't capture and long types, ...
        # but for now returning int is relatively safe
        tokens = [x.spelling for x in self.get_initialization().get_tokens()]
        if tokens[0] == "unsigned":
            return "unsigned"
        return "int"

    def cond_end_value(self):
        ''' Return the For iteration end expression. '''

        # FIXME: Probably it just work with positive numbers
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
            startindex = tokens.index(">")
            addition = " + 1"
        elif tokens.count("<=") == 1:
            startindex = tokens.index("<=")
        elif tokens.count(">=") == 1:
            startindex = tokens.index(">=")
        else:
            raise NotImplementedError(
                "Just implemented for loops with simple conditions"
            )

        return ("(" + " ".join(tokens[startindex + 1: endindex]) +
                addition + ")")

    def is_affine(self):
        ''' Return whether this loop is affine. '''
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


    def variable_analysis(self):
        '''
        For each variable inside the loop body differentiate between:

        1. Local variables: Variables declared and used only in the loop scope.

        2. Modified global variables: Variables with global scope modified
        within the loop.

        3. Arrays/Pointers read.

        4. Run-time Invariants: Variables with global scope but not modified
        in the loop.

        '''
        local_vars = []
        local_vars_names = []
        other_vars = []
        other_vars_names = []
        written_scalars = []
        written_scalars_names = []
        runtime_constants = []

        # 1. Find local variables: any declaration inside the loop.
        for decl in self.find_declarations():
            local_vars.append(decl)
            local_vars_names.append(decl.displayname)

        # 2. Find outer-scope variables that are written in the loop.
        for assignment in self.find_assignments():

            # Get the assignment LHS
            var = assignment.get_children()[0]

            # Get only the top-level object in member operations
            while var.kind == CursorKind.MEMBER_REF_EXPR:
                var = var.get_children()[0]

            # Also recurse down if lhs has operators (e.g. pointer dereference)
            while var.kind == CursorKind.UNARY_OPERATOR:
                var = var.get_children()[0]

            # Avoid duplicates, reference that are local, and pointer or arrays
            if var.displayname not in local_vars_names and \
               var.displayname not in written_scalars_names and \
               var.kind != CursorKind.ARRAY_SUBSCRIPT_EXPR and \
               not var.type_is_pointer():
                written_scalars.append(var)
                written_scalars_names.append(var.displayname)

        # 3. Find outer-scope arrays read in the loop
        # (raw pointers are added in the loop below).
        # for array in self.find_array_accesses():

            # Recurse down in case it is a multidimensional array
        #    while array.displayname == "":
        #        array = array.get_children()[0]

            # Avoid duplicates and local variables
        #    if array.displayname not in other_vars_names and \
        #       array.displayname not in local_vars_names:
        #        other_vars.append(array)
        #        other_vars_names.append(array.displayname)

        # 4. Variables which we know are invariants between loop iterations:
        # This are only scalars at the moment
        runtime_constants = []
        runtime_constants_names = []
        for access in self.find_all_accesses():

            # FIXME
            if access.spelling == "operator=":
                continue

            # Recurse down in UNEXPOSED_EXPR until the displayname is already
            # the same as the children.
            while len(access.get_children()) > 0 and \
                    access.kind == CursorKind.UNEXPOSED_EXPR:
                if access.get_children()[0].displayname == access.displayname:
                    access = access.get_children()[0]
                else:
                    break

            # Just consider the initial reference in a struct/class memeber
            # (e.g. ref_considered.ignore.ignore)
            while access.kind == CursorKind.MEMBER_REF_EXPR:
                access = access.get_children()[0]

            if access.displayname not in runtime_constants_names and \
               access.displayname not in local_vars_names and \
               access.displayname not in written_scalars_names and \
               access.displayname not in other_vars_names and \
               access.displayname != '' and \
               access.kind != CursorKind.CALL_EXPR:

                if access.type_is_scalar():
                    runtime_constants.append(access)
                    runtime_constants_names.append(access.displayname)
                else:
                    other_vars.append(access)
                    other_vars_names.append(access.displayname)

        return local_vars, other_vars, written_scalars, runtime_constants
