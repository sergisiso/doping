# pylint: disable=no-self-use, protected-access
''' Py.test tests for the DopingCursors class hierarchy as implemented in
ast/cursor.py '''

import os
import pytest
from codegen.ast.translation_unit import DopingTranslationUnit
from codegen.ast.cursors import DopingCursor


class TestDopingCursorBase:
    ''' Test the DopingCursor base class '''

    @pytest.fixture
    def sample_cursor(self, tmpdir):
        ''' Creates a temporary file called test.c with helloworld'''
        filename = os.path.join(str(tmpdir), "test.c")
        with open(filename, "w") as source:
            source.write(
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
        sampletu = DopingTranslationUnit(filename)
        return sampletu.get_root()

    def test_cursor_base(self, sample_cursor):
        ''' Test '''
        assert isinstance(sample_cursor, DopingCursor)
