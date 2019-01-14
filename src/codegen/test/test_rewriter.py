

''' Py.test tests for the Rewriter class as implemented in Rewriter.py '''

import os
import pytest
from codegen.Rewriter import Rewriter


class TestRewriter(object):

    @pytest.fixture
    def samplefile(self, tmpdir):
        ''' Creates a temporary file called test.txt with 3 lines '''
        filename = os.path.join(str(tmpdir), "test.txt")
        with open(filename, "w") as f:
            f.write("Original1\n")
            f.write("Original2\n")
            f.write("Original3\n")
        return filename

    @pytest.fixture
    def sampleRewriter(self, tmpdir):
        ''' Creates a Rewriter object with a non-existent file '''
        fn = os.path.join(str(tmpdir), "empty.txt")
        return Rewriter(fn)

    @pytest.fixture
    def rewriterObj(self, samplefile):
        ''' Creates a Rewriter object with the sample file '''
        return Rewriter(samplefile)

    @pytest.fixture
    def rewriterObjMod(self, rewriterObj):
        ''' Applies multiple modifications to a Rewriter Object '''
        rewriterObj.goto_line(2)
        rewriterObj.insert("Insert1")
        rewriterObj.goto_line(4)
        rewriterObj.insert("Insert2")
        rewriterObj.goto_line(3)
        rewriterObj.delete()
        return rewriterObj

    def test_init_existing_file(self, samplefile):
        ''' Class contructor with an existing file '''
        obj = Rewriter(samplefile)
        assert obj._filename == samplefile
        assert obj._ind_level == 0

    def test_init_nonexistent_file(self, tmpdir):
        ''' Class contructor with an non-existing file '''
        fn = os.path.join(str(tmpdir), "nonexistent.txt")
        obj = Rewriter(fn)
        assert obj._filename == fn
        assert obj._original_num_lines == 0
        assert len(obj._content) == 0
        assert len(obj._deltas) == 0
        assert obj._cursor == 1
        assert obj._ind_level == 0

    def test_load_from_file(self, samplefile, sampleRewriter):
        ''' Load the contents or a file '''
        fn = sampleRewriter._filename  # load should not change the filename
        sampleRewriter.load(samplefile)
        assert sampleRewriter._filename == fn
        assert sampleRewriter._original_num_lines == 3
        assert sampleRewriter._content[1] == "Original2"
        assert sampleRewriter._deltas == [0, 0, 0]
        assert sampleRewriter._cursor == 1
        assert sampleRewriter._next_original_delta_index == [0, 1, 2]

    def test_get_content(self, rewriterObj):
        ''' Get the line  '''  # TODO: Change method name
        assert "Original1" == rewriterObj.get_content()

    def test_goto_line_in_range(self, rewriterObj):
        ''' Puts the cursor into the specified line '''
        assert rewriterObj.get_line() == 1
        rewriterObj.goto_line(2)
        assert rewriterObj.get_line() == 2
        assert rewriterObj.get_content() == "Original2"

    def test_goto_line_out_of_range(self, rewriterObj):
        ''' Tests goto_line raises the appropiate Errors when Out of range '''
        with pytest.raises(IndexError):
            rewriterObj.goto_line(-2)

        with pytest.raises(IndexError):
            rewriterObj.goto_line(0)

        with pytest.raises(IndexError):
            rewriterObj.goto_line(4)

        rewriterObj.goto_line(3)  # Should not raise an exception

    def test_goto_original_line_out_of_range(self, rewriterObj):
        ''' Tests goto_original_line raises the appropiate Errors
        when Out of range '''
        with pytest.raises(IndexError):
            rewriterObj.goto_original_line(-1)

        with pytest.raises(IndexError):
            rewriterObj.goto_original_line(0)

        with pytest.raises(IndexError):
            rewriterObj.goto_original_line(4)

        rewriterObj.goto_original_line(3)

    def test_goto_original_line(self, rewriterObj):
        ''' Put cursor where the original line is/was in the buffer '''
        rewriterObj.goto_original_line(1)
        assert rewriterObj._cursor == 1
        rewriterObj.goto_original_line(3)
        assert rewriterObj._cursor == 3

    def test_insert(self, rewriterObj, sampleRewriter):
        ''' Insert new line into the buffer, at the cursor position '''

        # Insert to an empty buffer
        sampleRewriter.insert("Insert1")
        assert "Insert1" in sampleRewriter._content[0]
        assert sampleRewriter._cursor == 2

        rewriterObj.goto_line(2)
        rewriterObj.insert("Insert1")
        assert "Insert1" in rewriterObj._content[rewriterObj._cursor - 2]
        # -2 comes from -1 for cursor advance + -1 from 1-indexed
        assert rewriterObj._deltas == [0, 1, 1]
        assert rewriterObj._cursor == 3
        assert rewriterObj._content == ['Original1', 'Insert1',
                                        'Original2', 'Original3']
        assert rewriterObj._next_original_delta_index == [0, 1, 1, 2]

        rewriterObj.goto_line(4)
        rewriterObj.insert("Insert2")
        assert "Insert2" in rewriterObj._content[rewriterObj._cursor - 2]
        assert rewriterObj._deltas == [0, 1, 2], str(rewriterObj._content)
        assert rewriterObj._cursor == 5
        assert rewriterObj._next_original_delta_index == [0, 1, 1, 2, 2]

        rewriterObj.goto_line(2)
        rewriterObj.insert("Insert3")
        assert "Insert3" in rewriterObj._content[rewriterObj._cursor - 2]
        assert rewriterObj._deltas == [0, 2, 3], str(rewriterObj._content)
        assert rewriterObj._cursor == 3
        assert rewriterObj._next_original_delta_index == [0, 1, 1, 1, 2, 2]

    def test_delete(self, rewriterObj):
        ''' Deletes from the buffer the line at the cursor position '''
        rewriterObj.goto_line(2)
        rewriterObj.delete()
        assert rewriterObj._content == ['Original1', 'Original3']
        assert rewriterObj._cursor == 2
        assert rewriterObj._deltas == [0, 0, -1]
        assert rewriterObj._next_original_delta_index == [0, 2]

    def test_goto_original_line_integration(self, rewriterObjMod):
        ''' Integration test of multiple insert/delete operations '''
        rewriterObjMod.goto_original_line(1)
        assert rewriterObjMod._cursor == 1
        rewriterObjMod.goto_original_line(2)
        assert rewriterObjMod._cursor == 3, str(rewriterObjMod._content)
        rewriterObjMod.goto_original_line(3)
        assert rewriterObjMod._cursor == 4, str(rewriterObjMod._content)
