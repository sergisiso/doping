

''' Py.test tests for the DopingCursorBase class as
implemented in DopingAST/DopingCursor.py '''

import os
import pytest
from codegen.DopingAST.DopingTranslationUnit import DopingTranslationUnit
from codegen.DopingAST.DopingCursors import DopingCursorBase


class TestDopingCursorBase(object):

    @pytest.fixture
    def sampleCursor(self, tmpdir):
        ''' Creates a temporary file called test.c with helloworld'''
        filename = os.path.join(str(tmpdir), "test.c")
        with open(filename, "w") as f:
            f.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n
                \n
                int main(){\n
                    printf("Hello World");\n
                    return 0;\n
                }\n
                '''
            )
        tu = DopingTranslationUnit(filename)
        return tu.get_root()

    def test_fixtures_are_CursorBase(self, sampleCursor):
        assert isinstance(sampleCursor, DopingCursorBase)
