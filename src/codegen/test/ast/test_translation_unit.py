# pylint: disable=no-self-use, protected-access
''' Py.test tests for the DopingTranslationUnit class as implemented in
ast/translation_unit.py '''

import os
import pytest
import clang
from codegen.ast.translation_unit import DopingTranslationUnit
from codegen.ast.cursors import DopingCursor


class TestDopingTranslationUnit:
    ''' Test the DopingTranslationUnit'''

    @pytest.fixture
    def invalidfile1(self, tmpdir):
        ''' Create a temporary file called test.txt with 3 lines '''
        filename = os.path.join(str(tmpdir), "test.txt")
        with open(filename, "w") as source:
            source.write("Invalid format\n")
        return filename

    @pytest.fixture
    def invalidfile2(self, tmpdir):
        ''' Create a invalid c file - missing a ;'''
        filename = os.path.join(str(tmpdir), "testinvalid.c")
        with open(filename, "w") as source:
            source.write(
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
        ''' Create a temporary valid c file'''
        filename = os.path.join(str(tmpdir), "testvalid.c")
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
        return filename

    def test_init_non_existent_file(self, tmpdir):
        ''' Test creating a translation unit of a non-existent file '''
        filename = os.path.join(str(tmpdir), "non-existent.c")
        with pytest.raises(FileNotFoundError):
            _ = DopingTranslationUnit(filename)

    def test_init_invalid_file(self, invalidfile1, invalidfile2):
        ''' Test creating a translation unit of an invalid C file '''

        # The file does not have the proper extension
        with pytest.raises(ValueError, match="Unrecognized file extension in .*"):
            _ = DopingTranslationUnit(invalidfile1)

        # Invalid C files are still parsed, is that ok?
        invalidtu = DopingTranslationUnit(invalidfile2)
        assert invalidtu._filename.endswith("testinvalid.c")
        assert isinstance(invalidtu._clang_tu, clang.cindex.TranslationUnit)

    def test_init_with_a_valid_c_file(self, cfile):
        ''' Test creating a translation unit of a valid C file '''
        filetu = DopingTranslationUnit(cfile)

        # The _filename and _clang_tu are set appropriately
        assert filetu._filename.endswith("testvalid.c")
        assert isinstance(filetu._clang_tu, clang.cindex.TranslationUnit)

    def test_init_with_compiler_command(self, cfile):
        ''' Test creating a translation unit of a valid C file '''
        _ = DopingTranslationUnit(cfile, "gcc -O2")

        # Check with an invalid compiler_command type
        with pytest.raises(TypeError, match="DopingTranslationUnit compiler_command "
                                            "parameter must be a string"):
            _ = DopingTranslationUnit(cfile, 123)

    def test_get_root(self, cfile):
        ''' The get_root() method returns a doping cursor. '''
        sample_tu = DopingTranslationUnit(cfile)
        assert isinstance(sample_tu.get_root(), DopingCursor)

    def test_get_parse_arguments(self, cfile):
        ''' The get_parse_arguments() method returns the arguments string '''
        # Test with an empty list of arguments
        sample_tu = DopingTranslationUnit(cfile)
        assert isinstance(sample_tu.get_parse_arguments(), list)
        assert len(sample_tu.get_parse_arguments()) == 0

        # Test with multiple arguments, just the ones starting with '-' should appear
        sample_tu = DopingTranslationUnit(cfile, "gcc -O2 invalidflag")
        assert len(sample_tu.get_parse_arguments()) == 1
        assert "-O2" in sample_tu.get_parse_arguments()
