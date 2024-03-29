""" Implementation of InjectDoping transformation """

import os
from codegen.transformations.transformation import CodeTransformation


class InjectDoping(CodeTransformation):
    """ InjectDoping Transformation """
    # pylint: disable=too-few-public-methods, too-many-instance-attributes,
    # pylint: disable=too-many-statements, too-many-branches

    def __init__(self, inputfile, outputfile, compiler_command="", is_cpp=False):
        super().__init__(inputfile, outputfile, compiler_command)
        self.compiler_command = compiler_command
        self._loop_id = 0
        self._is_cpp = is_cpp

        # Globals shared between methods
        self._local_vars = None
        self._pointers = None
        self._written_scalars = None
        self._runtime_invariants = None
        self._fcalls = None

    def _candidates(self):
        return self._ast.find_loops(outermostonly=True, exclude_headers=True)

    def _static_analysis(self, node):
        print("Analyzing loop at " + str(node.location))

        # Special condition for Doping Benchmarking of TSVC test suite, ignore otherwise
        is_benchmark = os.getenv('DOPING_BENCHMARK')
        if is_benchmark == '1':
            if node.location.line < 910 or node.location.line > 5584:
                print("DISCARDED by DOPING_BENCHMARK (from 910 to 5584)")
                return False

        # Analyse the loop variables
        local_vars, pointers, written_scalars, runtime_constants = \
            node.variable_analysis()

        # Analyse the function calls
        fcalls = [x for x in node.find_calls()]

        self._print_analysis(local_vars, pointers, written_scalars,
                             runtime_constants, fcalls)

        if len(runtime_constants) < 1:
            print("    > No dynamic optimization applied.\n")
            return False

        print("    > Creating dynamically optimized version of the loop.\n")

        self._local_vars = local_vars
        self._pointers = pointers
        self._written_scalars = written_scalars
        self._runtime_invariants = runtime_constants
        self._fcalls = fcalls

        return True

    def _apply(self, node):

        # Get a unique id to this loop for this transformation
        self._loop_id = self._loop_id + 1

        # Choose signed or unsigned version iteration variable
        if node.cond_variable_type() == "int":
            iteration_type = "int"
            struct_type = "dopinginfo"
            rtfunc_name = "dopingRuntime"
        else:
            iteration_type = "unsigned"
            struct_type = "dopinginfoU"
            rtfunc_name = "dopingRuntimeU"

        # We will need to generate a string of values of the runtime invariants with
        # an sprintf call, e.g: `sprintf(dopingRuntimeVal_X, "A:%d,B:%f", A, B);`. So
        # we check that we can populate the format and parameters list here, otherwise
        # we refuse to optimize the loop.
        format_list = []
        parameters_list = []
        for var in self._runtime_invariants:
            format_specifier = None
            if var.type.spelling in ('int', 'short', 'long'):
                format_specifier = "%d"
            elif var.type.spelling in ('unsigned int', 'unsigned long'):
                format_specifier = "%u"
            elif var.type.spelling in ('float',):
                format_specifier = "%f"
            elif var.type.spelling in ('double',):
                format_specifier = "%lf"
            else:
                print("    > Tried dynamic optimization but found unsupported"
                      " type: {0}.\n".format(var.type.spelling))
                return False
            format_list.append(var.displayname + ":" + format_specifier)
            parameters_list.append(var.displayname)

        format_list.append("doping_restrict_all:%d")
        if len(self._pointers) > 1 and node.guarantee_non_aliasing_of(self._pointers):
            # TODO: We also need to test that is not in the range from start to iteration end!
            base = self._pointers[0].displayname
            cmp_address_string = " && ".join([base + "!=" + var.displayname for var in self._pointers[1:]])
            parameters_list.append(cmp_address_string)
        else:
            parameters_list.append("0")
        # TODO: Could also add an alignment check!

        # Include doping runtime at the top if it doesn't exist already
        self._buffer.goto_line(1)
        include_string = "#include \"doping.h\""
        if self._buffer.get_content() != include_string:
            self._buffer.insert(include_string)
            self._buffer.insert("#include <stdio.h>")

        # Comment old code
        self._buffer.goto_original_line(node.get_start())
        self._buffer.insert("//  ---- CODE TRANSFORMED BY doping ----")
        self._buffer.insert("//  ---- Old version from " + str(node.location) + "----")
        for _ in range((node.get_end() - node.get_start()) + 1):
            self._buffer.comment()

        # Generate new version of the loop in a new scope
        self._buffer.insert("")
        self._buffer.insert("//  ---- New version: ----")
        self._buffer.insert("{  // start a doping scope")

        # Convert runtime constant values into strings with sprintf
        # e.g:
        #     char dopingRuntimeVal_X[100];
        #     sprintf(dopingRuntimeVal_X, "A:%d,B:%f", A, B);

        # Create Unique string identifier
        parameters_string = "dopingRuntimeVal_" + str(self._loop_id)
        # Declare the string (array of char)
        self._buffer.insert("char " + parameters_string + "[300];")
        # Ensemble the sprinf call
        self._buffer.insert("sprintf(" + parameters_string + ", ")
        self._buffer.insertpl("\""+",".join(format_list) + "\", ")
        self._buffer.insertpl(", ".join(parameters_list) + ");")

        # Generate the dopinginfo object
        self._buffer.insert(struct_type + " info" + str(self._loop_id) + " = {")
        self._buffer.insert("    .iteration_start = " + node.cond_starting_value() + ",")
        self._buffer.insert("    .iteration_space = " + node.cond_end_value() + ",")
        self._buffer.insert("    .source = " + r'''"\n"''')
        # Insert the dynamic template of the code here (return the args that it will need)
        list_of_args = self._generate_dynamic_function(node, iteration_type)
        self._buffer.insertpl(",")
        # Continue dopinginfo object
        self._buffer.insert("    .compiler_command = " + "\"" +
                            self.compiler_command + "\"" + ",")
        self._buffer.insert("    .parameters = " + parameters_string + ",")
        self._buffer.insert("    .name = \"" + str(node.location) + "\",")
        self._buffer.insert("};")

        # Convert the loop into a while construct

        # First start with the initialization expression outside the while statement
        self._buffer.insert(node.initialization_string()+";")

        # Then the while construct with the Doping Runtime call
        # e.g.: while(dopingRuntime(i, i < 10, &info1, parameter1, parameter2 )){
        if len(list_of_args) == 0:
            list_of_args.append("NULL")
        self._buffer.insert("while(" + rtfunc_name + "(" +
                            node.cond_variable() + ", " +
                            node.end_condition_string() + ", " +
                            "&info" + str(self._loop_id) + ", " +
                            ", ".join(list_of_args))

        # self._buffer.insertpl(", " + node.cond_variable())
        # for var in self._pointers:
        #       self._buffer.insertpl(", " + var.displayname)

        self._buffer.insertpl(")){")
        self._buffer.increase_indexation()

        # Write original loop
        self._buffer.insert("")
        self._buffer.insert("// Unmodified loop")
        # If the loop had a pragma, insert it back
        if node.location.line in self._for_loop_pragmas:
            self._buffer.insert(self._for_loop_pragmas[node.location.line])

        self._buffer.insert("for(; (" + node.end_condition_string())
        # self._buffer.insertpl(" ) && time(NULL) < "+timevar+";")
        self._buffer.insertpl(" );")
        self._buffer.insertpl(node.increment_string() + ")")
        self._buffer.increase_indexation()
        self._buffer.insertpl(node.body_string())  # This breaks indentation
        self._buffer.decrease_indexation()
        self._buffer.decrease_indexation()
        self._buffer.insert("} //end while loop")
        self._buffer.insert("} //close doping scope")
        self._buffer.insert("")
        return True

    def _replicate_preprocessor(self, node, remove_includes=False):
        """ Return all the proprocessor statements before and after
        the selected node."""

        before = []
        after = []
        inside_comment = False

        with open(self._inputfile) as source:
            lines = source.readlines()
            for lnum, line in enumerate(lines):
                if line.replace(" ", "").startswith("#") and not inside_comment:
                    if remove_includes and line.startswith('#include'):
                        continue
                    # FIXME: What about multi-line (symbol \ continuation)
                    # FIXME: Are some #pragma necessary (e.g. #pragma once)?
                    if not line.startswith('#pragma'):
                        if lnum < node.location.line - 1:
                            before.append(line)
                        else:
                            after.append(line)
                if "/*" in line and "*/"not in line:
                    inside_comment = True
                if "*/" in line and "/*" not in line:
                    inside_comment = False
                # FIXME: What about these symbols inide strings: printf("\\*");
                # FIXME: What about multiple comments in the same line, e.g:
                # /* Comment 1 */ /* Comment 2 */
        return before, after

    def _generate_dynamic_function(self, node, iteration_type):
        """ Insert the dynamic function template string and return the
        variadic arguments that the created function will need."""


        method = "method2"

        # Required libs
        self._buffer.insertstr("#include <stdarg.h>")
        remove_other_includes = False

        if method == "method2":
            cwd = os.getcwd()
            incpath = os.path.join(cwd, node.location.file.name)
            self._buffer.insertstr(f"#include \"{incpath}\"")
            remove_other_includes = True

        # Replicate preprocessor macros until this point
        before, after = self._replicate_preprocessor(node, remove_other_includes)

        for line in before:
            self._buffer.insertstr(line.replace('\n', ''))  # Remove \n

        if method == "method1":

            # Function calls can be:
            # - External (will be defined in the headers that are already copied)
            # - Be in the original file (found at link time if the -rdynamic -ldl are
            # included)
            # - Be in the original file and have the attributes static and/or inline.
            # We need to copy these ones over to the dynamically optimized code.
            inlined_functions = []
            for func in self._fcalls:
                func_def = func.find_definition()
                if func_def is not None:
                    print(f"    - Function '{func_def.spelling}' definition found in "
                          f"{func_def.location}")

                    # FIXME: In AO func_def.spelling != func_def.get_tokens() !??
                    tokens = [x.spelling for x in func_def.get_tokens()]
                    attributes = []
                    # if tokens:
                    #    attributes.extend(tokens[:tokens.index(func.spelling)])

                    # We could inline other functions if everything that they contain
                    # is defined inside the function (has no globals or function calls).
                    # FIXME: In fact this also affect the static inline functions below.

                    # FIXME: Actually the inlined or signatures should be in the appropriate
                    # place regarding the preprocessor statements, it should be merged with
                    # the _replicate_preprocessor functionality.

                    # Store/mark this function as already inlined
                    if func_def not in inlined_functions:
                        inlined_functions.append(func_def)
                    for line in func_def.get_string().split('\n'):
                        self._buffer.insertstr(line)
                    continue
                    if 'static' in attributes or 'inline' in attributes:
                        # FIXME: Check for function calls also inside func
                        for line in func_def.get_string().split('\n'):
                            self._buffer.insertstr(line)
                    else:
                        # Insert just the function signature
                        self._buffer.insertstr(func_def.result_type.spelling + " " +
                                               func_def.displayname + ";")
                else:
                    found = False
                    for file_func_decl in self._ast.find_functions():
                        if file_func_decl.spelling == func.spelling:
                            found = True

                            # Store/mark this function as already inlined
                            if file_func_decl not in inlined_functions:
                                inlined_functions.append(file_func_decl)

                            # Insert just the function signature
                            for line in file_func_decl.get_string().split('\n'):
                                self._buffer.insertstr(line)

                            print("    - Only the function signature of ", func.spelling,
                                  " was found!")
                    if not found:
                        print(f"    - Declaration of function '{func.spelling}' in "
                              f"{func.location}  not found. Assuming it is defined "
                              "in imported headers.")

        # Always use the C ABI
        if self._is_cpp:
            self._buffer.insertstr(r'extern "C" void function(')
        else:
            self._buffer.insertstr(r"void function(")

        self._buffer.insertstr(iteration_type + " dopingCurrentIteration,")
        self._buffer.insertstr("va_list args){")

        # TODO: Pass arguments by reference and use statement below ?
        # https://wiki.sei.cmu.edu/confluence/display/c/MSC39-C.+Do+not+call+
        # va_arg%28%29+on+a+va_list+that+has+an+indeterminate+value
        # self._buffer.insertstr("va_list args; va_copy(args, *arguments);")

        # Declare local variables
        # for var in local_vars:
        #    vtype = var.type.spelling
        #    self._buffer.insertstr(vtype + " " + var.displayname + ";")

        # Write a DOPING substitution template to specialize runtime invariants
        for invar in self._runtime_invariants:
            if self._is_cpp:
                qualifier = "constexpr "
            else:
                qualifier = "const "
            self._buffer.insertstr(qualifier + invar.type.spelling + " " +
                                   invar.displayname +
                                   " = /*<DOPING " +
                                   invar.displayname + " >*/;")

        # Get pointers or arrays used in the loop
        list_of_va_args = []
        for pointer in self._pointers:
            pointer_type = pointer.type.spelling
            # TODO: We currently lose the dimension information here:
            # e.g: const float [4] -> const float a*;

            # Argument array declaration symbol in not valid in a declaration
            # statement, transform to pointer syntax.
            dims = pointer_type.count('[')
            if dims > 0:
                first_square_bracket = pointer_type.index('[')
                pointer_type = pointer_type[:first_square_bracket] + ("*" * dims)

            # Variadic type macro expansion fails if it has the restrict attribute,
            # so we remove it
            va_type = pointer_type.replace('__restrict','')

            # Write a conditional Doping string to add __restrict when possible
            restrict_string = " /*<DOPING_IF doping_restrict_all __restrict__ >*/ "

            self._buffer.insertstr(pointer_type + restrict_string + pointer.displayname +
                                   " = va_arg(args, " + va_type + ");")
            # self._buffer.insertstr(pointer.displayname + " = (" + pointer_type + ")" +
            #        "__builtin_assume_aligned(" + pointer.displayname + ",64);")
            list_of_va_args.append(pointer.displayname)

        # Get written_scalars (passed by reference - as a pointer)
        # Since in C we can not create aliases(&) we need to prefix all
        # references to this variable with the C * operator in:
        # node.get_* functions in the loop body and conditions.
        ref_vars = []
        for var in self._written_scalars:
            vtype = var.type.spelling + "*"  # Add pointer indetifier
            self._buffer.insertstr(vtype + " " + var.displayname + "_dopingglobal" +
                                   " = va_arg(args, " + vtype + ");")
            list_of_va_args.append("&" + var.displayname)
            # FIXME: This assumes no aliasing in this scalar, this need proper runtime
            # checks.
            self._buffer.insertstr(var.type.spelling + " " + var.displayname + " = " +
                                   "(*" + var.displayname + "_dopingglobal);")
            ref_vars.append(var.displayname)

        # If the loop had a pragma, insert it back
        if node.location.line in self._for_loop_pragmas:
            self._buffer.insertstr(self._for_loop_pragmas[node.location.line])

        self._buffer.insertstr_nolb(
            "for(" + node.cond_variable_type() + " " + node.cond_variable() +
            " = dopingCurrentIteration;" + node.end_condition_string() + "; " +
            node.increment_string() + ")")

        # for line in node.body_string(referencing_variables=ref_vars).split("\n"):
        for line in node.body_string().split("\n"):
            self._buffer.insertstr(line)

        for var in self._written_scalars:
            self._buffer.insertstr("(*" + var.displayname + "_dopingglobal) = " +
                                   var.displayname + ";")
        self._buffer.insertstr('}')

        # There can be open pre-processor conditionals that need closing after
        # the function
        for line in after:
            self._buffer.insertstr(line.replace("\n", ''))

        return list_of_va_args

    @staticmethod
    def _print_analysis(local_vars, pointers, written_scalars,
                        runtime_constants, fcalls):
        print("    Local vars:")
        for var in local_vars:
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Arrays/Pointers:")
        for pointer in pointers:
            var = pointer
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Scalar writes:")
        for var in written_scalars:
            if not var.displayname:
                print(var.displayname)
                print(var.spelling)
                print(var)
                print(var.location)
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Vars for delayed evaluation:")
        for var in runtime_constants:
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Number of function calls: " + str(len(fcalls)))
        for func in fcalls:
            print("    Function:" + func.displayname)
