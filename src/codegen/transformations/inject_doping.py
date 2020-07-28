""" Implementation of InjectDoping transformation """

import os
from codegen.transformations.transformation import CodeTransformation


class InjectDoping(CodeTransformation):
    """ InjectDoping Transformation """
    # pylint: disable=too-few-public-methods

    def __init__(self, inputfile, outputfile, compiler_command="", is_cpp=False):
        super(InjectDoping, self).__init__(inputfile, outputfile, compiler_command)
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
        return self._ast.find_loops(True, True)

    def _static_analysis(self, node):
        print("Analyzing loop at " + str(node.location))

        # Special condition for Doping Benchmarking of TSVC test suite, ignore otherwise
        is_benchmark = os.getenv('DOPING_BENCHMARK')
        if is_benchmark == '1':
            if node.location.line < 910 or node.location.line > 5584:
                return False

        # Analyse the loop variables
        local_vars, pointers, written_scalars, runtime_constants = \
                node.variable_analysis()

        # Analyse the function calls
        fcalls = node.function_call_analysis()

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

        # Get a unique id in this file for this transformation
        self._loop_id = self._loop_id + 1

        # Choose signed or unsigned version
        if node.cond_variable_type() == "int":
            iteration_type = "int"
            struct_type = "dopinginfo"
            rtfunc_name = "dopingRuntime"
        else:
            iteration_type = "unsigned"
            struct_type = "dopinginfoU"
            rtfunc_name = "dopingRuntimeU"

        # Include doping runtime at the top if it doesn't exist already
        self._buffer.goto_line(1)
        include_string = "#include \"doping.h\""
        if self._buffer.get_content() != include_string:
            self._buffer.insert(include_string)
            self._buffer.insert("#include <stdio.h>")

        # Comment old code
        self._buffer.goto_original_line(node.get_start())
        self._buffer.insert("//  ---- CODE TRANSFORMED BY doping ----")
        self._buffer.insert("//  ---- Old version from " + str(node.location) + "----------")
        for _ in range((node.get_end() - node.get_start()) + 1):
            self._buffer.comment()
        self._buffer.insert("")

        # Generate new version of the loop
        self._buffer.insert("//  --------- New version: ----------")
        self._buffer.insert("{  // start a doping scope")

        # Convert runtime constant values into strings with sprintf
        # e.g:
        #     char dopingRuntimeVal_X[100];
        #     sprintf(dopingRuntimeVal_X, "A:%d,B:%f", A, B);

        # Create Unique string identifier
        parameters_string = "dopingRuntimeVal_" + str(self._loop_id)
        # Declare the string (array of char)
        self._buffer.insert("char " + parameters_string + "[100];")
        # Populate the format and parameters list
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
                      " type.\n")
                return False
            format_list.append(var.displayname + ":" + format_specifier)
            parameters_list.append(var.displayname)
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
        self._buffer.insert("    .compiler_command = " + "\"" + self.compiler_command + "\"" + ",")
        self._buffer.insert("    .parameters = " + parameters_string + ",")
        self._buffer.insert("    .name = \"" + str(node.location) + "\",")
        self._buffer.insert("};")

        # Convert the loop into a while construct
        # First start with the initialization expression
        self._buffer.insert(node.initialization_string()+";")

        # Then the while construct with the Doping Runtime call
        self._buffer.insert("while(" + rtfunc_name + "(" +
                            node.cond_variable() + ", " +
                            node.end_condition_string() + ", " +
                            "&info" + str(self._loop_id) + ", " +
                            ", ".join(list_of_args))

        if False:
            self._buffer.insertpl(", " + node.cond_variable())
            for var in self._pointers:
                self._buffer.insertpl(", " + var.displayname)

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

    def _replicate_preprocessor(self, node):
        """ Return all the proprocessor statements before and after
        the selected node."""

        before = []
        after = []
        inside_comment = False

        with open(self._inputfile) as source:
            lines = source.readlines()
            for lnum, line in enumerate(lines):
                if line.replace(" ", "").startswith("#") and not inside_comment:
                    # FIXME: What about multi-line (symbol \ continuation)
                    # FIXME: Are some #pragma necessary (e.g. #pragma once)?
                    if not line.startswith('#pragma'):
                        if lnum < node.location.line - 1:
                            before.append(line)
                        else:
                            after.append(line)
                if "/*" in line and not "*/" in line:
                    inside_comment = True
                if "*/" in line and not "/*" in line:
                    inside_comment = False
                # FIXME: What about these symbols inide strings: printf("\\*");
                # FIXME: What about multiple comments in the same line, e.g:
                # /* Comment 1 */ /* Comment 2 */
        return before, after


    def _generate_dynamic_function(self, node, iteration_type):
        """ Insert the dynamic function template string and return the
        variadic arguments that the created function will need."""

        # Required libs
        self._buffer.insertstr("#include <stdarg.h>")

        # Replicate preprocessor macros until this point
        before, after = self._replicate_preprocessor(node)
        for line in before:
            self._buffer.insertstr(line.replace('\n','')) # Remove \n

        # Function calls can be:
        # - External (will be defined in the headers that are already copied)
        # - Be in the original file (found at link time if the -rdymaic -ldl are included)
        # - Be in the original file and have the attributes static and/or inline. We need to
        #   copy these ones over to the dynamically optimized code.
        for func in self._fcalls:
            func_def = func.get_definition()
            if func_def is not None:
                tokens = [x.spelling for x in func.get_definition().get_tokens()]
                attributes = tokens[:tokens.index(func.spelling)]
                # FIXME: Actually the inlined or signatures should be in the appropriate
                # place regarding the preprocessor statements, it should be merged with
                # the _replicate_preprocessor functionality.
                if 'static' in attributes or 'inline' in attributes:
                    # FIXME: Check for function calls also inside func
                    for line in func.get_definition().get_string().split('\n'):
                        self._buffer.insertstr(line)
                else:
                    # Insert just the function signature
                    self._buffer.insertstr(func_def.result_type.spelling + " " +
                                           func_def.displayname + ";")

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
        #for var in local_vars:
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

            self._buffer.insertstr(pointer_type + " " + pointer.displayname +
                                   " = va_arg(args, " + pointer_type + ");")
            list_of_va_args.append(pointer.displayname)

        # Get written_scalars (passed by reference - as a pointer)
        # Since in C we can not create aliases(&) we need to prefix all
        # references to this variable with the C * operator in:
        # node.get_* functions in the loop body and conditions.
        ref_vars = []
        for var in self._written_scalars:
            vtype = var.type.spelling + "*"  # Add pointer indetifier
            self._buffer.insertstr(vtype + " " + var.displayname +
                                   " = va_arg(args, " + vtype + ");")
            list_of_va_args.append("&" + var.displayname)
            ref_vars.append(var.displayname)

        # If the loop had a pragma, insert it back
        if node.location.line in self._for_loop_pragmas:
            self._buffer.insertstr(self._for_loop_pragmas[node.location.line])

        self._buffer.insertstr_nolb(
            "for(" + node.cond_variable_type() +  " " + node.cond_variable() +
            " = dopingCurrentIteration;" + node.end_condition_string() + "; " +
            node.increment_string() + ")")

        for line in node.body_string(referencing_variables=ref_vars).split("\n"):
            self._buffer.insertstr(line)
        self._buffer.insertstr('}')

        # There can be open pre-processor conditionals that need closing after
        # the function
        for line in after:
            self._buffer.insertstr(line.replace("\n", ''))

        return list_of_va_args


    @staticmethod
    def _print_analysis(local_vars, pointers, written_scalars,
                        runtime_constants, fcalls):
        stop = False
        print("    Local vars: ")
        for var in local_vars:
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Arrays/Pointers: ")
        for pointer in pointers:
            var = pointer
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Scalar writes: ")
        for var in written_scalars:
            if not var.displayname:
                print(var.displayname)
                print(var.spelling)
                print(var)
                print(var.location)
                stop = True
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Vars for delayed evaluation: ")
        for var in runtime_constants:
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Number of function calls: " + str(len(fcalls)))
        # if stop:
        #     exit(-1)
