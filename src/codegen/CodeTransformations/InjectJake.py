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



