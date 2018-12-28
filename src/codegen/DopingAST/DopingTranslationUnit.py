import os
from clang.cindex import Index
from codegen.DopingAST.DopingCursors import DopingCursorBase

class DopingTranslationUnit():

    filename = None
    TU = None

    def __init__(self, filename):
        if not os.path.isfile(filename):
            raise FileNotFoundError("{0} does not exist".format(filename))
        extension = os.path.splitext(filename)[1]
        if extension not in (".c",".cc",".cpp"):
            raise ValueError("Unrecognized file extension in {0}".format(filename))

        self.filename = filename
        index = Index.create()
        self.TU = index.parse(filename)

    def get_root(self):
        root = self.TU.cursor
        root.__class__ = DopingCursorBase
        return root
