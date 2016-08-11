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


