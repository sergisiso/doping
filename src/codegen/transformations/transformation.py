from codegen.rewriter import Rewriter
from codegen.ast.translation_unit import DopingTranslationUnit


class CodeTransformation:

    _inputfile = None
    _outputfile = None
    _ast = None
    _buffer = None
    _flags = None
    _for_loop_pragmas = {}

    def __init__(self, inputfile, outputfile, flags):
        self._inputfile = inputfile
        self._outputfile = outputfile
        self._flags = flags
        self._store_for_pragmas(inputfile)

    def apply(self):
        print("Compilation parsing flags:", self._flags)
        tu = DopingTranslationUnit(self._inputfile, self._flags)
        self._ast = tu.get_root()
        result = []
        for loop in self._candidates():
            if self._static_analysis(loop):
                if self._buffer is None:
                    self._buffer = Rewriter(self._outputfile)
                    self._buffer.load(self._inputfile)

                ret = self._apply(loop)
                self._buffer.save()
                result.append((loop.location, ret))
            else:
                result.append((loop.location, False))

    def _candidates(self):
        raise NotImplementedError(
            "This is an abstract class, instantiate a subclass!"
        )

    def _apply(self, node):
        raise NotImplementedError(
            "This is an abstract class, instantiate a subclass!"
        )

    def _static_analysis(self, node):
        raise NotImplementedError(
            "This is an abstract class, instantiate a subclass!"
        )

    def _store_for_pragmas(self, filename):
        with open(filename) as source:
            lines = source.readlines()
            for lnum, line in enumerate(lines):
                if line.replace(" ", "").startswith("#pragma"):
                    if lines[lnum + 1].replace(" ", "").startswith("for"):
                        # Another +1 for the 1-indexing of line numbers
                        self._for_loop_pragmas[lnum + 1 + 1] = line[:-1]
