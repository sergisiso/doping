from codegen.Rewriter import Rewriter
from codegen.CodeTransformations.CodeTransformation import CodeTransformation


class InjectDoping(CodeTransformation):

    def __init__(self, inputfile, outputfile, compiler_command=""):
        super(InjectDoping, self).__init__(inputfile, outputfile, compiler_command)
        self.compiler_command = compiler_command
        self._loop_id = 0

    def _candidates(self):
        return self._ast.find_loops(True, True)

    def _static_analysis(self, node):
        return True

    def _apply(self, node):

        print("Analyzing loop at " + str(node.location))
        self._loop_id = self._loop_id + 1
        loop_id = self._loop_id

        # Analyse the loop variables
        local_vars, pointers, written_scalars, runtime_constants = \
                node.variable_analysis()

        # Analyse the function calls
        fcalls = node.function_call_analysis()

        self._print_analysis(local_vars, pointers, written_scalars,
                             runtime_constants, fcalls)

        if len(runtime_constants) < 1 or len(fcalls) > 0:
            print("    > No dynamic optimization applied.\n")
            return False

        print("    > Creating dynamically optimized version of the loop.\n")

        # Choose signed or unsigned version
        if node.cond_variable_type() == "int":
            iteration_type = "int"
            struct_type = "dopinginfo"
            rtfunc_name = "dopingRuntime"
        else:
            iteration_type = "unsigned"
            struct_type = "dopinginfoU"
            rtfunc_name = "dopingRuntimeU"

        # Include doping runtime
        self._buffer.goto_line(1)
        include_string = "#include \"doping.h\""
        if self._buffer.get_content() != include_string:
            self._buffer.insert(include_string)

        # Comment old code
        self._buffer.goto_original_line(node.get_start())
        self._buffer.insert("//  ---- CODE TRANSFORMED BY doping ----")
        self._buffer.insert("//  --------- Old version: ----------")
        for _ in range((node.get_end() - node.get_start()) + 1):
            self._buffer.comment()
        self._buffer.insert("")

        # Generate new version of the loop
        self._buffer.insert("//  --------- New version: ----------")
        self._buffer.insert("{  // start a doping scope")

        # Convert runtime constant values into strings with sprintf
        # if len(runtime_constants) > 0  # For now this is always true

        # Unique string identifier
        parameters_string = "dopingRuntimeVal_" + str(loop_id)
        # Declare the string (array of char)
        self._buffer.insert("char " + parameters_string + "[100];")
        # Populate with a sprintf call
        format_list = []
        parameters_list = []
        for idx, var in enumerate(runtime_constants):
            format_specifier = None
            if var.type.spelling in ('int', 'short', 'long'):
                format_specifier = "%d"
            elif var.type.spelling in ('unsigned int', 'unsigned long'):
                format_specifier = "%u"
            elif var.type.spelling in ('float'):
                format_specifier = "%f"
            elif var.type.spelling in ('double'):
                format_specifier = "%lf"
            else:
                print("    > Tried dynamic optimization but found unsupported"
                      " type.\n")
                return False

            format_list.append(var.displayname + ":" + format_specifier)
            parameters_list.append(var.displayname)
        self._buffer.insert("sprintf(" + parameters_string + ", ")
        self._buffer.insertpl("\""+",".join(format_list) + "\", ")
        self._buffer.insertpl(", ".join(parameters_list) + ");")


        # 1) Generate the dopinginfo object
        self._buffer.insert(struct_type + " info" + str(loop_id) + " = {")
        self._buffer.insert("    .iteration_start = " +
                            node.cond_starting_value() + ",")
        self._buffer.insert("    .iteration_space = " +
                            node.cond_end_value() + ",")
        self._buffer.insert("    .source = " + r'''"\n"''')

        # Dynamic versrion of the code

        # Write function definition with pointers and written_scalars
        for include in node.find_file_includes():
            self._buffer.insertstr(include[:-1])  # [:-1] to remove the \n
        self._buffer.insertstr("#include <cstdarg>")
        self._buffer.insertstr("#include <stdio.h>")

        # Write local functions called from the body loop.
        # for f in node.function_call_analysis():
        #    self._buffer.insert(" ".join([x.spelling for x in
        #                                  f.get_definition().get_tokens()]))

        self._buffer.insertstr(r"extern \"C\" void function(")
        self._buffer.insertstr(iteration_type + " dopingCurrentIteration,")
        self._buffer.insertstr("va_list args){")

        # TODO: Pass arguments by reference and use statement below ?
        # https://wiki.sei.cmu.edu/confluence/display/c/MSC39-C.+Do+not+call+
        # va_arg%28%29+on+a+va_list+that+has+an+indeterminate+value
        # self._buffer.insertstr("va_list args; va_copy(args, *arguments);")

        # Declare local variables
        for var in local_vars:
            vtype = var.type.spelling
            self._buffer.insertstr(vtype + " " + var.displayname + ";")

        # Write delayed evaluated invariants
        for invar in runtime_constants:
            self._buffer.insertstr("const " + invar.type.spelling + " " +
                                   invar.displayname +
                                   " = /*<DOPING " +
                                   invar.displayname + " >*/;")

        # Get pointers
        list_of_va_args = []
        for pointer in pointers:
            pointer_type = pointer.type.spelling
            self._buffer.insertstr(pointer_type + " " + pointer.displayname +
                                   " = va_arg(args, " + pointer_type + ");")
            list_of_va_args.append(pointer.displayname)

        # Get written_scalars (passed by reference - as a pointer)
        # Since in C we can not create aliases(&) we need to prefix all
        # references to this variable with the C * operator in:
        # node.get_* functions in the loop body and conditions.
        ref_vars = []
        for var in written_scalars:
            vtype = var.type.spelling + "*"  # Add pointer indetifier
            self._buffer.insertstr(vtype + " " + var.displayname +
                                   " = va_arg(args, " + vtype + ");")
            list_of_va_args.append("&" + var.displayname)
            ref_vars.append(var.displayname)

        self._buffer.insertstr_nolb(
            "for(" + node.cond_variable_type() +  " " + node.cond_variable() +
            " = dopingCurrentIteration;" + node.end_condition_string() + "; " +
            node.increment_string() + ")")

        for line in node.body_string(referencing_variables=ref_vars).split("\n"):
            self._buffer.insertstr(line)

        self._buffer.insert(r'''"}\n",''')

        # Continue dopinginfo object

        self._buffer.insert("    .compiler_command = " + "\"" + self.compiler_command + "\"" + ",")
        self._buffer.insert("    .parameters = " + parameters_string + ",")
        self._buffer.insert("};")

        # 2) Loop starting value
        self._buffer.insert(node.initialization_string()+";")

        # 3) Doping Runtime call
        self._buffer.insert("while(" + rtfunc_name + "(" +
                            node.cond_variable() + ", " +
                            node.end_condition_string() + ", " +
                            "&info" + str(loop_id) + ", " +
                            ", ".join(list_of_va_args))

        if False:
            self._buffer.insertpl(", " + node.cond_variable())
            for var in pointers:
                self._buffer.insertpl(", " + var.displayname)

        self._buffer.insertpl(")){")
        self._buffer.increase_indexation()

        # Write original loop with time exit condition
        self._buffer.insert("")
        self._buffer.insert("// Unmodified loop")
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

    def _post_transformation(self):
        # Add necessary includes
        self._buffer.goto_line(1)
        self._buffer.insert("#include <time.h>")
        self._buffer.insert("#include <dlfcn.h>")
        self._buffer.insert("#include <stdio.h>")
        self._buffer.insert("#include <stdlib.h>")
        self._buffer.insert("#include \"../../src/runtime/dopingRuntime.h\"")

    @staticmethod
    def _print_analysis(local_vars, pointers, written_scalars,
                        runtime_constants, fcalls):
        print("    Local vars: ")
        for var in local_vars:
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Arrays/Pointers: ")
        for pointer in pointers:
            var = pointer.get_children()[0]
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Scalar writes: ")
        for var in written_scalars:
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Vars for delayed evaluation: ")
        for var in runtime_constants:
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Number of function calls: " + str(len(fcalls)))
