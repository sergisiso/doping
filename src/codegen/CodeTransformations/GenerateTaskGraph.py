from codegen.Rewriter import Rewriter
from codegen.AST import ASTNode
from CodeTransformation import CodeTransformation


class GenerateTaskGraph (CodeTransformation):

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
	    file.insert("tVar( "+local_var[v]+", "+v+");")

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



