import os
from clang.cindex import Index
from codegen.DopingAST.DopingCursors import DopingCursorBase


class DopingTranslationUnit():
    '''
    This class encapsulates Clang Translation unit functionality.
    When the class is instantiated, it already parsed the provided file.
    '''

    _filename = None
    _TU = None

    def __init__(self, filename):
        if not os.path.isfile(filename):
            raise FileNotFoundError("{0} does not exist".format(filename))
        extension = os.path.splitext(filename)[1]
        if extension not in (".c", ".cc", ".cpp"):
            raise ValueError(
                "Unrecognized file extension in {0}".format(filename)
            )

        self._filename = filename
        index = Index.create()
        self._TU = index.parse(filename)

    def get_root(self):
        '''
        Returns the DopingCursor that represents the AST root node.
        '''
        root = self._TU.cursor
        root.__class__ = DopingCursorBase
        return root
