import os
from subprocess import call
from codegen.Rewriter import Rewriter
from codegen.AST import ASTNode
from CodeTransformation import CodeTransformation

class InjectJake (CodeTransformation):

    def __init__(self, filename):
        self.filename = filename

    def _apply(self):
        # Shortcuts
        file = self.file
        ast = self.ast

        # Get first loop
	candidates = list(ast.find_loops(True))
	if len(candidates) < 1:
		print("No candidates found for transformation")
		return
	node = candidates[0]
        print( "-> Generating taskgraph for loop at " + node.str_position())


        # Add header and Comment old code
        file.goto_line(node.get_start())
        file.insert("//  --------- CODE TRANSFORMED BY JAKE ----------")
        file.insert("//  --------- Old version: ----------")
        for i in range((node.get_end() - node.get_start())+1):
            self.file.comment()

        # Generate new version of the loop
        file.insert("//  --------- New version: ----------")
        if node.isFor():
            for_loop = node

            file.insert("time_t JAKEend, JAKElast;")
            file.insert("JAKEend = time(NULL) + 2;")
            file.insert("JAKElast = time(NULL);")
            #file.insert("struct timespec JAKEend, JAKElast;")
            #file.insert("clock_gettime(CLOCK_MONOTONIC, &JAKEend);")
            #file.insert("clock_gettime(CLOCK_MONOTONIC, &JAKEend);")
            #file.insert("clock_gettime(CLOCK_MONOTONIC, &JAKElast);")
            
            #Create profiled version
            file.insert(" ".join(for_loop.get_init_tokens()))
            file.insert("for(;")
            newcond = for_loop.get_cond_tokens()
            newcond.insert( 0, "(")
            newcond.insert(-1, " ) && JAKElast < JAKEend")
            file.insertpl(" ".join(newcond))
            file.insertpl(" ".join(for_loop.get_incr_tokens()))
            file.increase_indexation()
            newbody = for_loop.get_body_tokens()
            #newbody.insert(-1,"clock_gettime(CLOCK_MONOTONIC, &JAKElast);")
            newbody.insert(-1,"JAKElast = time(NULL);")
            file.insert(" ".join(newbody))
            file.decrease_indexation()
        
        # Runtime analysis
            file.insert("float JAKEprogress = float(" + for_loop.cond_variable())
            file.insertpl(")/(" + for_loop.cond_end_value()  +" - ")
            file.insertpl(for_loop.cond_starting_value() + ");")
            file.insert("std::cout << \"Loop at interation \" << x << \" (\" ")
            file.insertpl("<< JAKEprogress * 100 << \"%)\" << std::endl ;")
            file.insert("std::cout << \"Estimation of Loop total time: \" <<")
            file.insertpl(" 2/JAKEprogress << \"secs\" << std::endl ;")

        # Create new version
            
            fname, fext = os.path.splitext(self.filename)
            newfname = fname+".loop"+fext
            print "Writing "+ newfname

            local_var, tg_input_vars, del_eval = self.static_var_analysis(node)

            if os.path.isfile(newfname): os.remove(newfname)
            jakefile = Rewriter(newfname)

            funcdecl = "extern \"C\" void loop("

            for vname, vtype in tg_input_vars.items():
                
                match = vtype.find('[')
                if match > 0:
                    basetype = vtype[:match]
                    arrayext = vtype[match:]
                    funcdecl = funcdecl + basetype + " " + vname + arrayext + ","
                else:
                    funcdecl = funcdecl + vtype + " " + vname + ","

            funcdecl = funcdecl[0:-1] + "){"
    
            jakefile.insert(funcdecl)
            

            for vname, vtype in local_var.items():
                jakefile.insert(vtype+" "+vname+";")
                
            for vname, vtype in del_eval.items():
                jakefile.insert(vtype+" "+vname+" = JAKEPLACEHOLDER_"+vname+";")

            jakefile.insert("for(;")
            jakefile.insertpl(" ".join(for_loop.get_cond_tokens()))
            jakefile.insertpl(" ".join(for_loop.get_incr_tokens()))
            jakefile.increase_indexation()
            jakefile.insert(" ".join(for_loop.get_body_tokens()))
            jakefile.decrease_indexation()

            jakefile.insert("}")

            jakefile.save()
            jakefile.printall()
        

            print os.path.abspath(newfname), os.path.abspath(fname)
            

            file.insert("std::cout << \"I am here\" << std::endl;")        
            # Replace runtime constants
            if len(del_eval) > 0:
                spec_string = "char * specfname = specialize_function("
                spec_string = spec_string + "\"" +newfname+ "\"" + ", " + str(len(del_eval))
                for vname, vtype in del_eval.items():
                    file.insert("char JAKEstring"+vname+"[10];")
                    file.insert("sprintf(JAKEstring"+vname+",\"%d\","+vname+");")
                    spec_string = spec_string + ", \"" + vname + "\", JAKEstring"+vname 

                file.insert(spec_string+");")
            file.insert("std::cout << \"I am here2\" << specfname << std::endl;")        
            file.insert("char * command;")
            file.insert("system(\"g++ -fPIC -shared \"+specfname+\" -o \"+specfname+\".so\");")

            file.insert("std::cout << \"I am here3\" << std::endl;")        
            def_func_ptr = "typedef void (*pf)("
            for vname, vtype in tg_input_vars.items():
                def_func_ptr = def_func_ptr + vtype + ","
            def_func_ptr = def_func_ptr[:-1] + ");"
            file.insert(def_func_ptr)


            file.insert("const char * err;")
            file.insert("void * lib = dlopen(\""+fname+".so\", RTLD_NOW);")
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
            for vname, vtype in tg_input_vars.items():
                callstring = callstring + vname + ","
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

        else:
            print("No loop")



