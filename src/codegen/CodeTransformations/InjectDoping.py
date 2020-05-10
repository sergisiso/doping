from codegen.Rewriter import Rewriter
from codegen.CodeTransformations.CodeTransformation import CodeTransformation


class InjectDoping(CodeTransformation):

    def __init__(self, inputfile, outputfile, compiler_command=""):
        super(InjectDoping, self).__init__(inputfile, outputfile)
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
        l, p, w, r = node.variable_analysis()
        local_vars = l
        pointers = p
        written_scalars = w
        runtime_constants = r

        # Analyse the function calls
        fcalls = node.function_call_analysis()

        self._print_analysis(local_vars, pointers, written_scalars,
                             runtime_constants, fcalls)

        if len(runtime_constants) < 1 or len(fcalls) > 0:
            print("    > No dynamic optimization applied.\n")
            return False

        print("    > Creating dynamically optimized version of the loop.\n")

        # Choose signed or unsigned version
        integer_type = node.cond_variable_type() # int/unsigned or raises error
        if integer_type == "int":
            struct_type = "dopinginfo"
            rtfunc_name = "dopingRuntime"
        else:
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
            format_list.append(var.displayname + ":%d")
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

        self._buffer.insertstr(r"extern \"C\" void function(va_list args){")

        self._buffer.insertstr(r"printf(\"I am in\\n\"); fflush(stdout);")
        # Get loop start condition
        self._buffer.insertstr("unsigned lstart = va_arg(args, unsigned);")
        self._buffer.insertstr(r"printf(\"I am in\\n\"); fflush(stdout);")

        # Get pointers
        for a in pointers:
            atype = a.type.spelling
            self._buffer.insertstr(atype + " " + a.displayname +
                                   " = va_arg(args, " + atype + ");")

        # Declare additional vars
        for v in written_scalars:
            vtype = v.type.spelling
            self._buffer.insertstr(vtype + " " + v.displayname + ";")

        # Write delayed evaluated variables
        for v in runtime_constants:
            self._buffer.insertstr("const " + v.type.spelling + " " +
                                   v.displayname +
                                   " = /*<DOPING " +
                                   v.displayname + " >*/;")

        self._buffer.insertstr(r"printf(\"I am in\\n\"); fflush(stdout);")
        # if(self.verbosity_level==4):
        # self._buffer.insert("printf(\"Executing doping" +
        # " optimized version. Restart from iteration" +
        # " %d\\n \", lstart);")

        self._buffer.insertstr_nolb(
            "for( unsigned " + node.cond_variable() + " = lstart;" +
            node.end_condition_string() + "; " + node.increment_string() + ")")

        for line in node.body_string().split("\n"):
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
                            node.cond_variable())

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
