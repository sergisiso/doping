import os
from subprocess import call
from codegen.Rewriter import Rewriter
from codegen.CodeTransformations.CodeTransformation import CodeTransformation


class InjectDoping (CodeTransformation):

    # def __init__(self, filename, flags, verbosity):
    def __init__(self, inputfile, outputfile, flags=""):
        super(InjectDoping, self).__init__(inputfile, outputfile)
        # self.filename = filename
        self.flags_string = flags
        # self.verbosity_level = verbosity
        self._LoopID = 0

    def _candidates(self):
        return self._ast.find_loops(True, True)

    def _static_analysis(self, node):
        return True

    def _apply(self, node):

        print("Loop at " + str(node.location))
        self._LoopID = self._LoopID + 1
        LoopID = self._LoopID

        # Filter loop with local function calls (otherwise
        # will be copied in the optimized object file)
        # if len(node.function_call_analysis()) > 0: continue

        # Classify the loop variables
        l, p, w, r = node.variable_analysis()
        local_vars = l
        pointers = p
        written_scalars = w
        runtime_constants = r

        self._print_analysis(local_vars, pointers,
                             written_scalars, runtime_constants)
        if len(runtime_constants) < 1:
            return False
        else:
            print("    Creating dynamically optimized version of the loop.")

        # Include doping runtime
        self._buffer.goto_line(1)
        include_string = "#include \"doping.h\""
        if self._buffer.get_content() != include_string:
            self._buffer.insert(include_string)

        # Comment old code
        self._buffer.goto_original_line(node.get_start())
        self._buffer.insert("//  ---- CODE TRANSFORMED BY doping ----")
        self._buffer.insert("//  --------- Old version: ----------")
        for i in range((node.get_end() - node.get_start()) + 1):
            self._buffer.comment()
        self._buffer.insert("")

        # Generate new version of the loop
        self._buffer.insert("//  --------- New version: ----------")
        # 1) Generate the dopinginfo object
        self._buffer.insert("dopinginfo info" + str(LoopID) + " = {")
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
        for f in node.function_call_analysis():
            self._buffer.insert(" ".join([x.spelling for x in
                                          f.get_definition().get_tokens()]))

        self._buffer.insertstr(r"extern \"C\" void loop(va_list args){")

        # Get loop start condition
        self._buffer.insertstr("unsigned lstart = va_arg(args, unsigned);")

        # Get pointers
        for a in pointers:
            atype = a.type.spelling
            self._buffer.insertstr(atype + " " + a.displayname +
                                   " = va_arg(args, " + atype + ");")
            # self._buffer.insert("double *__restrict__ " +
            # a.displayname + " = va_arg(args, " \

        # Declare additional vars
        for v in written_scalars:
            vtype = v.type.spelling
            self._buffer.insertstr(vtype + " " + v.displayname + ";")

        # Write delayed evaluated variables
        for v in runtime_constants:
            self._buffer.insertstr("const " + v.type.spelling + " " +
                                   v.displayname +
                                   " = dopingPLACEHOLDER_" +
                                   v.displayname + ";")

        # if(self.verbosity_level==4):
        # self._buffer.insert("printf(\"Executing doping" +
        # " optimized version. Restart from iteration" +
        # " %d\\n \", lstart);")

        self._buffer.insertstr("for( unsigned " + node.cond_variable()
                               + " = lstart;" + node.end_condition_string()
                               + ";" + node.increment_string() + ")")

        for line in node.body_string().split("\n"):
            self._buffer.insertstr(line)

        self._buffer.insertstr("}}")

        self._buffer.insert(r'''"}\n",''')

        # Continue dopinginfo object

        self._buffer.insert("    .compiler_command = " + "\" \"" + ",")
        self._buffer.insert("    .parameters = " + "\" \"" + ",")
        self._buffer.insert("};")
        # self._buffer.insertpl(", \"" + self.flags_string + "\"")

        if False:  # Old code which I may need
            timevar = "dopingEnd"+str(LoopID)
            rtvar = "dopingRuntimeVal_"+str(LoopID)
            self._buffer.insert("time_t "+timevar+";")
            self._buffer.insert("char " + rtvar + "[" +
                                str(len(runtime_constants))+"][20];")
            for idx, var in enumerate(runtime_constants):
                self._buffer.insert("sprintf(" + rtvar + "[" + str(idx) +
                                    "], \"%d\" ," + var.displayname + ");")

        # 2) Loop starting value
        self._buffer.insert(node.initialization_string()+";")

        # 3) Doping Runtime call
        self._buffer.insert("while ( dopingRuntime(" +
                            node.cond_variable() + ", " +
                            node.end_condition_string() + ", " +
                            "&info" + str(LoopID))
        if False:
            # Add tuples of name and values of the runtime
            # constant variables
            # all in string format
            for idx, var in enumerate(runtime_constants):
                self._buffer.insertpl(", \"" + var.displayname + "\"" +
                                      ", "+rtvar+"[" + str(idx) + "]")

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
        self._buffer.insert(node.body_string())
        self._buffer.decrease_indexation()
        self._buffer.decrease_indexation()
        self._buffer.insert("}} //end while loop")
        self._buffer.insert("")

    def _post_transformation(self):
        # Add necessary includes
        self._buffer.goto_line(1)
        self._buffer.insert("#include <time.h>")
        self._buffer.insert("#include <dlfcn.h>")
        self._buffer.insert("#include <stdio.h>")
        self._buffer.insert("#include <stdlib.h>")
        self._buffer.insert("#include \"../../src/runtime/dopingRuntime.h\"")

    def _print_analysis(self, local_vars, pointers, written_scalars,
                        runtime_constants):
        print("    Local vars: ")
        for var in local_vars:
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Arrays/Pointers: ")
        for var in pointers:
            v = var.get_children()[0]
            print("        " + v.displayname + " (" +
                  v.type.spelling + ")")
        print("    Scalar writes: ")
        for var in written_scalars:
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("    Vars for delayed evaluation: ")
        for var in runtime_constants:
            print("        " + var.displayname + " (" +
                  var.type.spelling + ")")
        print("")
