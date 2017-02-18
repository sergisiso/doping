import os
from subprocess import call
from codegen.Rewriter import Rewriter
from codegen.AST import ASTNode
from CodeTransformation import CodeTransformation

class InjectJake (CodeTransformation):

    def __init__(self, filename, flags, verbosity):
        self.filename = filename
        self.flags_string = flags
        self.verbosity_level = verbosity

    def _apply(self):
        file = self.file

        # Get loops in the file
        candidates = list(self.ast.find_file_loops(True))
        if len(candidates) < 1:
            print("No candidates found for transformation")
            return
        
        LoopID = 0
        for node in candidates:
            print( "  -> Analysing loop at " + node.str_position())
            LoopID = LoopID + 1
            
            # Classify the loop variables
            local_vars, arrays, written_scalars, runtime_constants = node.variable_analysis()
            self._print_analysis(local_vars, arrays, written_scalars, runtime_constants)
            if len(runtime_constants) < 1: continue
            
            # Create new file for the specific loop
            fname, fext = os.path.splitext(self.filename)
            newfname = fname + ".loop" + str(LoopID) + fext
            print "    Writing new version of the loop at " + newfname
            if os.path.isfile(newfname): os.remove(newfname)
            jakefile = Rewriter(newfname)


            # Comment old code
            file.goto_original_line(node.get_start())
            file.insert("//  --------- CODE TRANSFORMED BY JAKE ----------")
            file.insert("//  --------- Old version: ----------")
            for i in range((node.get_end() - node.get_start())+1):
                self.file.comment()
            file.insert("")

            # Generate new version of the loop
            file.insert("//  --------- New version: ----------")
            timevar = "JAKEEnd"+str(LoopID)
            rtvar = "JAKERuntimeVal_"+str(LoopID)
            file.insert("time_t "+timevar+";")
            file.insert("char "+rtvar+"["+str(len(runtime_constants))+"][20];")
            for idx, var in enumerate(runtime_constants):
                file.insert("sprintf("+rtvar+"["+str(idx)+"], \"%d\" ,"+var.displayname+");")
            file.insert(node.get_init_string()+";")
            file.insert("while ( JakeRuntime( \""+ newfname +"\"")
            file.insertpl(","+str(self.verbosity_level)+" ")
            file.insertpl(", \"" + self.flags_string + "\"")
            file.insertpl(", &" + timevar)
            file.insertpl(", &" + node.cond_variable())
            file.insertpl(", " + node.cond_starting_value() + ", " + node.cond_end_value())
            file.insertpl(", " + node.get_cond_string() + ", " + str(len(runtime_constants)))
            # Add tuples of name and values of the runtime constant variables
            # all in string format
            for idx, var in enumerate(runtime_constants):
                file.insertpl(", \"" + var.displayname + "\"" + ", "+rtvar+"[" + str(idx) + "]")

            file.insertpl(", " + node.cond_variable())
            for var in arrays:
                file.insertpl(", " + var.displayname)

            file.insertpl(")){" )
            file.increase_indexation()

            # Write original loop with time exit condition
            file.insert("")
            file.insert("// Unmodified loop")
            file.insert("for(; (" + node.get_cond_string())
            file.insertpl(" ) && time(NULL) < "+timevar+";")
            file.insertpl(node.get_incr_string())
            file.increase_indexation()
            file.insert(node.get_body_string())
            file.decrease_indexation()
            file.decrease_indexation()
            file.insert("} //end while loop")
            file.insert("")

            # Write function definition with arrays and written_scalars
            jakefile.insert("#include <cstdarg>")
            jakefile.insert("#include <stdio.h>")
            jakefile.insert("extern \"C\" void loop(va_list args){")
            
            #Get loop start condition
            jakefile.insert("unsigned lstart = va_arg(args, unsigned);")
            
            #Get arrays
            for a in arrays:
                atype = a.type.spelling
                jakefile.insert(atype + " " + a.displayname + " = va_arg(args, " \
                #jakefile.insert("double *__restrict__ " + a.displayname + " = va_arg(args, " \
                        + atype + ");")

            #Declare additional vars
            for v in written_scalars:
                vtype = v.type.spelling
                jakefile.insert(vtype + " " + v.displayname + ";")

            # Write delayed evaluated variables
            for v in runtime_constants:
                jakefile.insert("const " + v.type.spelling + " " + \
                        v.displayname+" = JAKEPLACEHOLDER_"+v.displayname+";")

            if(self.verbosity_level==4):
                jakefile.insert("printf(\"Executing Jake optimized version. Restart from iteration %d\\n \", lstart);")

            jakefile.insert("for( unsigned " + node.cond_variable() + " = lstart;" + node.get_cond_string() + ";" + \
                   node.get_incr_string() + node.get_body_string())

            jakefile.insert("}")

            jakefile.save() # Not to confuse with 'file' which is saved by
                            # the superclass
            print("")

            
        # Add necessary includes
        file.goto_line(1)
        file.insert("#include <time.h>")
        file.insert("#include <dlfcn.h>")
        file.insert("#include <stdio.h>")
        file.insert("#include <stdlib.h>")
        file.insert("#include \"../../src/runtime/JakeRuntime.h\"")

    def _print_analysis(self, local_vars, arrays, written_scalars, runtime_constants):
        print ("    Local vars: ")
        for var in local_vars:
            print "        "+ var.displayname + " ("+ var.type.spelling + ")"
        print ("    Arrays: " )
        for var in arrays:
            v = var.get_children()[0]
            print "        "+ v.displayname + " ("+ v.type.spelling + ")"
        print ("    Scalar writes: " )
        for var in written_scalars:
            print "        "+ var.displayname + " ("+ var.type.spelling + ")"
        print ("    Vars for delayed evaluation: " )
        for var in runtime_constants:
            print "        "+ var.displayname + " ("+ var.type.spelling + ")"
        print("")


