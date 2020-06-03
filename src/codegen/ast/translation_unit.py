""" Docstring """


import os
from clang.cindex import Index
from codegen.ast.cursors import DopingCursor


class DopingTranslationUnit():
    '''
    This class encapsulates Clang Translation unit functionality.
    When the class is instantiated, it already parsed the provided file.
    '''

    _filename = None
    _TU = None

    def __init__(self, filename, compiler_command=None):
        if not os.path.isfile(filename):
            raise FileNotFoundError("{0} does not exist".format(filename))
        extension = os.path.splitext(filename)[1]
        if extension not in (".c", ".cc", ".cpp"):
            raise ValueError(
                "Unrecognized file extension in {0}".format(filename)
            )

        parse_arguments = ""
        if compiler_command:
            if not isinstance(compiler_command, str):
                raise TypeError(
                    "DopingTranslationUnit compiler_flags parameter must be "
                    "a string")
            parse_arguments = \
                [x for x in compiler_command.split() if x.startswith("-")]
        else:
            parse_arguments = ""

        self._filename = filename
        index = Index.create()
        self._TU = index.parse(filename, args=parse_arguments)

    def get_root(self):
        '''
        Returns the DopingCursor that represents the AST root node.
        '''
        root = self._TU.cursor
        root.__class__ = DopingCursor
        return root
