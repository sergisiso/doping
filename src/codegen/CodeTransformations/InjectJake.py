import os
from subprocess import call
from codegen.Rewriter import Rewriter
from codegen.AST import ASTNode
from CodeTransformation import CodeTransformation

class InjectJake (CodeTransformation):

    def __init__(self, filename):
        self.filename = filename

    def _apply(self):
        file = self.file

        # Get loops in the file
        candidates = list(self.ast.find_file_loops(True))
        if len(candidates) < 1:
            print("No candidates found for transformation")
            return
        
        LoopID = 0
        for node in candidates:
            print( "  -> Injecting Jake code at loop at " + node.str_position())
            LoopID = LoopID + 1

            # Comment old code
            file.goto_original_line(node.get_start())
            file.insert("//  --------- CODE TRANSFORMED BY JAKE ----------")
            file.insert("//  --------- Old version: ----------")
            for i in range((node.get_end() - node.get_start())+1):
                self.file.comment()

            # Generate new version of the loop
            file.insert("//  --------- New version: ----------")
            timevar = "JAKEEnd"+str(LoopID)
            file.insert("time_t "+timevar+";")

            #Create profiled version
            file.insert(" ".join(node.get_init_string()))
            file.insert("while (JakeRuntime(&"+timevar+",&" + node.cond_variable() \
                    + "," + " ".join(node.get_cond_string()[:-1]) + ")){" )
            file.increase_indexation()
            file.insert("// Unmodified loop")
            file.insert("for(;")
            newcond = node.get_cond_string()
            newcond.insert( 0, "(")
            newcond.insert(-1, " ) && time(NULL) < "+timevar)
            file.insertpl(" ".join(newcond))
            file.insertpl(" ".join(node.get_incr_string()))
            file.increase_indexation()
            file.insert(" ".join(node.get_body_string()))
            file.decrease_indexation()
            file.decrease_indexation()
            file.insert("}")

            # Create new version
            fname, fext = os.path.splitext(self.filename)
            newfname = fname+".loop"+fext
            print "Writing "+ newfname

            local_vars, arrays, written_scalars, runtime_constants = node.variable_analysis()

            if os.path.isfile(newfname): os.remove(newfname)
            jakefile = Rewriter(newfname)

            # Write function definition with arrays and written_scalars
            fndef = "extern \"C\" void loop("
            for v in arrays:
                fndef = fndef + v.type.spelling + " "+ v.displayname + ", "
            fndef = fndef[0:-2] + "){" # remove last coma and close statement

            print fndef
            jakefile.insert(fndef)

            
            # Write delayed evaluated variables
            for v in runtime_constants:
                jakefile.insert("const " + v.type.spelling + " " + \
                        v.displayname+" = JAKEPLACEHOLDER_"+v.displayname+";")
            jakefile.insert(node.get_string()[:-1])
            jakefile.insert("}")

            jakefile.save()
            jakefile.printall()

            print os.path.abspath(newfname), os.path.abspath(fname)

            
        # Add necessary includes
        file.goto_line(1)
        file.insert("#include <time.h>")
        file.insert("#include <dlfcn.h>")
        file.insert("#include <stdio.h>")
        file.insert("#include <stdlib.h>")
        file.insert("#include \"../../src/runtime/JakeRuntime.h\"")

