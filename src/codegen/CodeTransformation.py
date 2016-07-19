from codegen.Rewriter import Rewriter
from codegen.AST import ASTNode


class CodeTransformation:

    filename = None
    file = None
    ast = None

    def __init__(self):
        pass
    

    def static_analysis(self, line=None):
	self.ast =  ASTNode(filename=self.filename)
	ret = self._static_analysis(line)

    def apply(self):
        self.file = Rewriter(self.filename)
        self.ast = ASTNode(filename=self.filename)
        ret = self._apply()
        self.file.save()
        self.file.printall()
	return ret

    def _apply(self):
        raise NotImplementedError("This is an abstract class, instantiate one subclass")

    def _static_analysis(self):
        raise NotImplementedError("This is an abstract class, instantiate one subclass")




class LoopProfiling (CodeTransformation):

    def __init__(self, filename):
        self.filename = filename

    def _apply(self):
        # Shortcuts
        file = self.file
        ast = self.ast

        # Get first loop
        node = list(ast.find_loops(True))[0]
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
            file.insert("for(;")
            file.insertpl(" ".join(for_loop.get_cond_tokens()))
            file.insertpl(" ".join(for_loop.get_incr_tokens()))
            file.increase_indexation()
            file.insert(" ".join(for_loop.get_body_tokens()))
            file.decrease_indexation()
        
        # Add necessary includes
            file.goto_line(1)
            file.insert("#include <time.h>")

        else:
            print("No loop")



class GenerateTaskGraph (CodeTransformation):

    def __init__(self, filename):
        self.filename = filename

    def static_var_analysis(self, node):
	""" Return the local variables (used only inside the loop) and
	the global variables readed and updated (used also outside the loop):
	  - Local variables are candidates for being declared with TaskGraph tVar()
	  - Global variables are candidates for beign input/output of TaskGraph call
		- Defined types just being read can be delay evaluated
	"""
	local_vars = {}
	tg_input_vars = {}

	# FIXME: Assumed no declarations with same name for now
	
	print(node)

	decl = node.find_declarations()
	for d in decl:
	    dnode = d
	    local_vars[dnode.varname] = dnode.datatype
	
	writes = node.find_writes()
	for w in writes:
	    if w not in local_vars: # FIXME: first element
	        tg_input_vars[w] = node.find_type(w)
	
	reads, reads_array = node.find_reads()

	for v in reads_array:
	     tg_input_vars[v] = self.ast.find_type(v)
	
		
	reads = [x for x in reads if x not in local_vars.keys()]
	reads = [x for x in reads if x not in tg_input_vars.keys()]

	print ("Local vars: " + str(local_vars) )
	print ("Input/Output vars: " + str(tg_input_vars) )
	print ("Vars for delayed evaluation: " + str(reads) )

	return local_vars, tg_input_vars


    def _apply(self):
        # Shortcuts
        file = self.file
        ast = self.ast

        # Get first loop
        node = list(ast.find_loops(True))[0]
        print( "-> Generating taskgraph for loop at " + node.str_position())

	local_var, tg_input_vars = self.static_var_analysis(node)

        # Add header and Comment old code
        file.goto_line(node.get_start())
        file.insert("//  --------- CODE TRANSFORMED BY JAKE ----------")
        file.insert("//  --------- Old version: ----------")
        for i in range((node.get_end() - node.get_start())+1):
            self.file.comment()


        # Generate TaskGraph Code
        file.insert("//  --------- TG version: ----------")
        tg_id = "tg0"
        tg_type = "tgtype"

        #FIXME: Automatically deduce Type
        file.insert("typedef SCALARTYPE MatrixType[MATRIXSIZE][MATRIXSIZE];")
        file.insert("typedef tg::TaskGraph<void")
	for v in tg_input_vars.keys():
		file.insertpl(", " + tg_input_vars[v])
	file.insertpl("> "+tg_type+";")
        file.insert(tg_type+" "+tg_id+";")
        file.insert("")

        # macro taskgraph(type, name, parameters)
        file.insert("taskgraph("+tg_type+", "+tg_id+", ")
	file.insertpl("tuple"+str(len(tg_input_vars))+"(")
	for v in tg_input_vars.keys():
	    file.insertpl(v)
	    file.insertpl(",")
	# Remove last comma
	file.goto_line(file.get_line()-1)
	file.replace(file.get_content()[0:-1])
	file.insertpl(") ) {")
        file.increase_indexation()
	
	# Define local variables
	for v in local_var.keys():
	    file.insert("tVar( "+v+", "+local_var[v]+");")

        self.libclang_to_tg(node,file)

        file.decrease_indexation()
        file.insert("}")

        #FIXME: Set compiler and flags from an argument
        file.insert(tg_id+".compile( tg::GCC);" )
        file.insert(tg_id+".execute(")
	for v in tg_input_vars.keys():
		file.insertpl(v)
	    	file.insertpl(",")
	# Remove last comma
	file.goto_line(file.get_line()-1)
	file.replace(file.get_content()[0:-1])
	file.insertpl(");")

        file.goto_line(1)
        file.insert("#include <TaskGraph>")
        file.goto_line(5)
        file.insert("using namespace tg;")


    def libclang_to_tg(self, node, file):

        if node.isFor():
            for_loop = node
            file.insert("tFor( " + for_loop.cond_variable() + ", " \
                    + for_loop.cond_starting_value() + "," + for_loop.cond_end_value() + "){")
            file.increase_indexation()
            self.libclang_to_tg(for_loop.get_body(),file)
            file.decrease_indexation()
            file.insert("}")
        elif node.isCompound():
            # What exaclty is COMPOUND_STMT? I only see one STMT
            for c in node.get_children():
                self.libclang_to_tg(c,file)
        else:
            file.insert(" ".join(node.get_tokens()))



