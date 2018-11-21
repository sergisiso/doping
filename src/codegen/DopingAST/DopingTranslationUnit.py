import os
from clang.cindex import Index
from codegen.DopingAST.DopingCursors import DopingCursorBase

class DopingTranslationUnit():

    filename = None
    TU = None

    def __init__(self, filename):
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"{filename} does not exist")
        extension = os.path.splitext(filename)[1]
        if extension not in (".c",".cc",".cpp"):
            raise ValueError(f"Unrecognized file extension in {filename}")

        self.filename = filename
        index = Index.create()
        self.TU = index.parse(filename)

    def get_root(self):
        root = self.TU.cursor
        root.__class__ = DopingCursorBase
        return root

    def get_file_cursor(self):
        pass

    def get_outermostloops_in_file(self):
        pass

    def get_includes(self):
        pass



        

