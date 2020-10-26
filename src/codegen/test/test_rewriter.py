# pylint: disable=protected-access,redefined-outer-name
''' Py.test tests for the Rewriter class as implemented in Rewriter.py '''

import os
import pytest
from codegen.rewriter import Rewriter


@pytest.fixture
def samplefile(tmpdir):
    ''' Creates a temporary file called test.txt with 3 lines '''
    filename = os.path.join(str(tmpdir), "test.txt")
    with open(filename, "w") as fobj:
        fobj.write("Original1\n")
        fobj.write("Original2\n")
        fobj.write("Original3\n")
    return filename

@pytest.fixture
def empty_rewriter(tmpdir):
    ''' Creates a Rewriter object with a non-existent file '''
    return Rewriter(os.path.join(str(tmpdir), "empty.txt"))

@pytest.fixture
def sample_rewriter(samplefile):
    ''' Creates a Rewriter object with the sample file '''
    return Rewriter(samplefile)

@pytest.fixture
def sample_rewriter_modified(sample_rewriter):
    ''' Applies multiple modifications to a Rewriter Object '''
    sample_rewriter.goto_line(2)
    sample_rewriter.insert("Insert1")
    sample_rewriter.goto_line(4)
    sample_rewriter.insert("Insert2")
    sample_rewriter.goto_line(3)
    sample_rewriter.delete()
    return sample_rewriter

def test_init_existing_file(samplefile):
    ''' Class contructor with an existing file '''
    obj = Rewriter(samplefile)
    assert obj._filename == samplefile
    assert obj._ind_level == 0

def test_init_nonexistent_file(tmpdir):
    ''' Class contructor with an non-existing file '''
    fname = os.path.join(str(tmpdir), "nonexistent.txt")
    obj = Rewriter(fname)
    assert obj._filename == fname
    assert obj._original_num_lines == 0
    assert len(obj._content) == 0
    assert len(obj._deltas) == 0
    assert obj._cursor == 1
    assert obj._ind_level == 0

def test_load_from_file(samplefile, sample_rewriter):
    ''' Load the contents or a file '''
    fname = sample_rewriter._filename  # load should not change the filename
    sample_rewriter.load(samplefile)
    assert sample_rewriter._filename == fname
    assert sample_rewriter._original_num_lines == 3
    assert sample_rewriter._content[1] == "Original2"
    assert sample_rewriter._deltas == [0, 0, 0]
    assert sample_rewriter._cursor == 1
    assert sample_rewriter._next_original_delta_index == [0, 1, 2]

def test_get_content(sample_rewriter):
    ''' Get the contents of the line where the cursor is located '''
    assert sample_rewriter.get_content() == "Original1"

def test_goto_line_in_range(sample_rewriter):
    ''' Puts the cursor into the specified line '''
    assert sample_rewriter.get_line() == 1
    sample_rewriter.goto_line(2)
    assert sample_rewriter.get_line() == 2
    assert sample_rewriter.get_content() == "Original2"

def test_goto_line_out_of_range(sample_rewriter):
    ''' Tests goto_line raises the appropiate Errors when Out of range '''
    with pytest.raises(IndexError):
        sample_rewriter.goto_line(-2)

    with pytest.raises(IndexError):
        sample_rewriter.goto_line(0)

    with pytest.raises(IndexError):
        sample_rewriter.goto_line(4)

    sample_rewriter.goto_line(3)  # Should not raise an exception

def test_goto_original_line_out_of_range(sample_rewriter):
    ''' Tests goto_original_line raises the appropiate Errors
    when Out of range '''
    with pytest.raises(IndexError):
        sample_rewriter.goto_original_line(-1)

    with pytest.raises(IndexError):
        sample_rewriter.goto_original_line(0)

    with pytest.raises(IndexError):
        sample_rewriter.goto_original_line(4)

    sample_rewriter.goto_original_line(3)

def test_goto_original_line(sample_rewriter):
    ''' Put cursor where the original line is/was in the buffer '''
    sample_rewriter.goto_original_line(1)
    assert sample_rewriter._cursor == 1
    sample_rewriter.goto_original_line(3)
    assert sample_rewriter._cursor == 3

def test_insert(sample_rewriter, empty_rewriter):
    ''' Insert new line into the buffer, at the cursor position '''

    # Insert to an empty buffer
    empty_rewriter.insert("Insert1")
    assert "Insert1" in empty_rewriter._content[0]
    assert empty_rewriter._cursor == 2

    sample_rewriter.goto_line(2)
    sample_rewriter.insert("Insert1")
    assert "Insert1" in sample_rewriter._content[sample_rewriter._cursor - 2]
    # -2 comes from -1 for cursor advance + -1 from 1-indexed
    assert sample_rewriter._deltas == [0, 1, 1]
    assert sample_rewriter._cursor == 3
    assert sample_rewriter._content == ['Original1', 'Insert1',
                                        'Original2', 'Original3']
    assert sample_rewriter._next_original_delta_index == [0, 1, 1, 2]

    sample_rewriter.goto_line(4)
    sample_rewriter.insert("Insert2")
    assert "Insert2" in sample_rewriter._content[sample_rewriter._cursor - 2]
    assert sample_rewriter._deltas == [0, 1, 2], str(sample_rewriter._content)
    assert sample_rewriter._cursor == 5
    assert sample_rewriter._next_original_delta_index == [0, 1, 1, 2, 2]

    sample_rewriter.goto_line(2)
    sample_rewriter.insert("Insert3")
    assert "Insert3" in sample_rewriter._content[sample_rewriter._cursor - 2]
    assert sample_rewriter._deltas == [0, 2, 3], str(sample_rewriter._content)
    assert sample_rewriter._cursor == 3
    assert sample_rewriter._next_original_delta_index == [0, 1, 1, 1, 2, 2]

def test_delete(sample_rewriter):
    ''' Deletes from the buffer the line at the cursor position '''
    sample_rewriter.goto_line(2)
    sample_rewriter.delete()
    assert sample_rewriter._content == ['Original1', 'Original3']
    assert sample_rewriter._cursor == 2
    assert sample_rewriter._deltas == [0, 0, -1]
    assert sample_rewriter._next_original_delta_index == [0, 2]

def test_goto_original_line_integration(sample_rewriter_modified):
    ''' Integration test of multiple insert/delete operations '''
    sample_rewriter_modified.goto_original_line(1)
    assert sample_rewriter_modified._cursor == 1
    sample_rewriter_modified.goto_original_line(2)
    assert sample_rewriter_modified._cursor == 3, str(sample_rewriter_modified._content)
    sample_rewriter_modified.goto_original_line(3)
    assert sample_rewriter_modified._cursor == 4, str(sample_rewriter_modified._content)
