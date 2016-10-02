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
        candidates = list(self.ast.find_file_loops(True))[:1]
        if len(candidates) < 1:
            print("No candidates found for transformation")
            return
        
        for node in candidates:
            print( "  -> Injecting Jake code at loop at " + node.str_position())

            # Comment old code
            file.goto_line(node.get_start())
            file.insert("//  --------- CODE TRANSFORMED BY JAKE ----------")
            file.insert("//  --------- Old version: ----------")
            for i in range((node.get_end() - node.get_start())+1):
                self.file.comment()

            # Generate new version of the loop
            file.insert("//  --------- New version: ----------")
            file.insert("time_t JAKEend, JAKElast;")
            file.insert("JAKEend = time(NULL) + 2;")
            file.insert("JAKElast = time(NULL);")
            #file.insert("struct timespec JAKEend, JAKElast;")
            #file.insert("clock_gettime(CLOCK_MONOTONIC, &JAKEend);")
            #file.insert("clock_gettime(CLOCK_MONOTONIC, &JAKEend);")
            #file.insert("clock_gettime(CLOCK_MONOTONIC, &JAKElast);")

            #Create profiled version
            file.insert(" ".join(node.get_init_string()))
            file.insert("for(;")
            newcond = node.get_cond_string()
            newcond.insert( 0, "(")
            newcond.insert(-1, " ) && JAKElast < JAKEend")
            file.insertpl(" ".join(newcond))
            file.insertpl(" ".join(node.get_incr_string()))
            file.increase_indexation()
            newbody = node.get_body_string()
            #newbody.insert(-1,"clock_gettime(CLOCK_MONOTONIC, &JAKElast);")
            newbody.insert(-1,"JAKElast = time(NULL);")
            file.insert(" ".join(newbody))
            file.decrease_indexation()

            # Runtime analysis
            file.insert("float JAKEprogress = float(" + node.cond_variable())
            file.insertpl(")/(" + node.cond_end_value()  +" - ")
            file.insertpl(node.cond_starting_value() + ");")
            file.insert("std::cout << \"Loop at interation \" << x << \" (\" ")
            file.insertpl("<< JAKEprogress * 100 << \"%)\" << std::endl ;")
            file.insert("std::cout << \"Estimation of Loop total time: \" <<")
            file.insertpl(" 2/JAKEprogress << \"secs\" << std::endl ;")

            #file.printall()

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

            
            #for vname, vtype in local_var.items():
            #    jakefile.insert(vtype+" "+vname+";")

            # Write delayed evaluated variables
            for v in runtime_constants:
                jakefile.insert("const " + v.type.spelling+" "+v.displayname+" = JAKEPLACEHOLDER_"+v.displayname+";")

            jakefile.insert(node.get_string()[:-1])

            #jakefile.insert("for(;")
            #jakefile.insertpl(" ".join(node.get_cond_tokens()))
            #jakefile.insertpl(" ".join(node.get_incr_tokens()))
            #jakefile.increase_indexation()
            #jakefile.insert(" ".join(node.get_body_tokens()))
            #jakefile.decrease_indexation()

            jakefile.insert("}")

            jakefile.save()
            jakefile.printall()


            print os.path.abspath(newfname), os.path.abspath(fname)


            file.insert("std::cout << \"I am here\" << std::endl;")        
            # Replace runtime constants
            if len(runtime_constants) > 0:
                spec_string = "char * specfname = specialize_function("
                spec_string = spec_string + "\"" +newfname+ "\"" + ", " + str(len(runtime_constants))
                for v in runtime_constants:
                    file.insert("char JAKEstring"+v.displayname+"[10];")
                    file.insert("sprintf(JAKEstring"+v.displayname+",\"%d\","+v.displayname+");")
                    spec_string = spec_string + ", \"" + v.displayname + "\", JAKEstring"+v.displayname 

                file.insert(spec_string+");")
            file.insert("std::string command = std::string(\"g++ -fPIC -shared \") + specfname + \" -o \" +specfname+ \".so\";")
            file.insert("std::cout << \"Compiling: \" << command << std::endl;")        
            file.insert("system(command.c_str());")
            #file.insert("system(\"g++ -fPIC -shared \"+specfname+\" -o \"+specfname+\".so\");")

            file.insert("std::cout << \"I am here3\" << std::endl;")        
            def_func_ptr = "typedef void (*pf)("
            for v in arrays:
                def_func_ptr = def_func_ptr + v.type.spelling + ","
            def_func_ptr = def_func_ptr[:-1] + ");"
            file.insert(def_func_ptr)


            file.insert("const char * err;")
            file.insert("void * lib = dlopen((specfname+std::string(\".so\")).c_str(), RTLD_NOW);")
            file.insert("if (!lib){")
            file.increase_indexation()
            file.insert("printf(\"failed to open library .so: %s \\n\", dlerror());")
            file.insert("exit(1);")
            file.decrease_indexation()
            file.insert("}dlerror();")
            file.insert("pf function = (pf) dlsym(lib, \"loop\");")
            file.insert("err = dlerror();")
            file.insert("if (err){")
            file.increase_indexation()
            file.insert("printf(\"failed to locate function: %s \\n\", err);")
            file.insert("exit(1);")
            file.decrease_indexation()
            file.insert("}")
            callstring = "function("
            for v in arrays:
                callstring = callstring + v.displayname + ","
            callstring = callstring[:-1] + ");"
            file.insert(callstring)
            file.insert("dlclose(lib);") 

        # Add necessary includes
            file.goto_line(1)
            file.insert("#include <time.h>")
            file.insert("#include <dlfcn.h>")
            file.insert("#include <stdio.h>")
            file.insert("#include <stdlib.h>")
            file.insert("#include \"../../src/runtime/JakeRuntime.h\"")

