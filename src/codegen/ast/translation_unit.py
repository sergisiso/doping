""" Docstring """


import os
from clang.cindex import Index
from codegen.ast.cursors import DopingRootCursor


class DopingTranslationUnit():
    '''
    This class encapsulates Clang Translation unit functionality.
    When the class is instantiated, it already parsed the provided file.
    '''

    _filename = None
    _clang_tu = None
    _parse_arguments = []

    def __init__(self, filename, compiler_command=None):
        if not os.path.isfile(filename):
            raise FileNotFoundError("{0} does not exist".format(filename))
        extension = os.path.splitext(filename)[1]
        if extension not in (".c", ".cc", ".cpp"):
            raise ValueError(
                "Unrecognized file extension in {0}".format(filename)
            )

        if compiler_command:
            if not isinstance(compiler_command, str):
                raise TypeError(
                    "DopingTranslationUnit compiler_command parameter must be "
                    "a string")
            self._parse_arguments = \
                [x for x in compiler_command.split() if x.startswith("-")]

        self._filename = filename
        index = Index.create()
        #print(filename, self._parse_arguments)
        #self._clang_tu = index.parse(filename, args=self._parse_arguments)
        self._clang_tu = index.parse(filename)

    def get_root(self):
        ''' Returns the DopingCursor that represents the AST root node. '''
        root = self._clang_tu.cursor
        root.__class__ = DopingRootCursor
        with open(self._filename, "r") as source:
            root._source_code = source.read()
        return root

    def get_parse_arguments(self):
        ''' Return arguments used by Clang to parse the source file. '''
        return self._parse_arguments
