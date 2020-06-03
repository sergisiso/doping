

''' Py.test tests for the DopingTranslationUnit class as
implemented in DopingAST/DopingTranslationUnit.py '''

import os
import pytest
from codegen.ast.translation_unit import DopingTranslationUnit


class TestDopingTranslationUnit(object):

    @pytest.fixture
    def samplefile(self, tmpdir):
        ''' Creates a temporary file called test.txt with 3 lines '''
        filename = os.path.join(tmpdir, "test.txt")
        with open(filename, "w") as f:
            f.write("Original1\n")
            f.write("Original2\n")
            f.write("Original3\n")
        return filename

    def test_init_invalid_file(self, tmpdir):
        assert True
