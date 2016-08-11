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
	        tg_input_vars[w] = self.ast.find_type(w)
	
	reads, reads_array = node.find_reads()

	for v in reads_array:
	     tg_input_vars[v] = self.ast.find_type(v)
	
		
	reads = [x for x in reads if x not in local_vars.keys()]
	reads = [x for x in reads if x not in tg_input_vars.keys()]

	print ("Local vars: " + str(local_vars) )
	print ("Input/Output vars: " + str(tg_input_vars) )
	print ("Vars for delayed evaluation: " + str(reads) )

	return local_vars, tg_input_vars, reads



