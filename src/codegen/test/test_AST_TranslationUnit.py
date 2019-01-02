''' Py.test tests for the DopingTranslationUnit class as
implemented in DopingAST/DopingTranslationUnit.py '''

import os
import pytest
from codegen.DopingAST.DopingTranslationUnit import DopingTranslationUnit


class TestDopingTranslationUnit(object):

    @pytest.fixture
    def invalidfile1(self, tmpdir):
        ''' Creates a temporary file called test.txt with 3 lines '''
        filename = os.path.join(str(tmpdir), "test.txt")
        with open(filename, "w") as f:
            f.write("Invalid format\n")
        return filename

    @pytest.fixture
    def invalidfile2(self, tmpdir):
        ''' Creates a invalid c file - missing a ;'''
        filename = os.path.join(str(tmpdir), "test.c")
        with open(filename, "w") as f:
            f.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n
                \n
                int main(){\n
                    printf("Hello World")\n
                    return 0;\n
                }\n
                '''
            )
        return filename

    @pytest.fixture
    def cfile(self, tmpdir):
        ''' Creates a temporary c file'''
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
        return filename

    @pytest.fixture
    def sampleTU(self, cfile):
        return DopingTranslationUnit(cfile)

    def test_init_non_existent_file(self, tmpdir):
        fn = os.path.join(str(tmpdir), "non-existent.c")
        with pytest.raises(FileNotFoundError):
            tu = DopingTranslationUnit(fn)

    def test_init_invalid_file(self, invalidfile1):
        with pytest.raises(ValueError):
            tu = DopingTranslationUnit(invalidfile1)

    def test_init_invalid_c_file(self, invalidfile2):
        import clang
        tu = DopingTranslationUnit(invalidfile2)
        assert tu._filename.endswith("test.c")
        assert isinstance(tu._TU, clang.cindex.TranslationUnit)
        # TODO: This should return and error
        # TODO: Add error handling

    def test_init_with_file(self, cfile):
        import clang
        tu = DopingTranslationUnit(cfile)
        assert tu._filename.endswith("test.c")
        assert isinstance(tu._TU, clang.cindex.TranslationUnit)
        # TODO: Check it is a properly parsed C/C++ file
        # assert False, str(tu.TU.cursor.spelling)

    def test_init_with_file(self, sampleTU):
        from codegen.DopingAST.DopingCursors import DopingCursorBase
        assert isinstance(sampleTU.get_root(), DopingCursorBase)
