""" This module provides a Rewritter buffer """

import os

class Rewriter:
    '''
    This class implements a 're-write buffer' as a list of lines
    and allows to insert/delete/replace lines. It also keep track
    of the position of the original lines, this allows to place the
    cursor using the current line numbers or the original line numbers.
    It is useful for making modifications in multiple locations of the
    buffer when the user only has references to the original line numbers
    (like the pre-parsed AST tree).
    '''

    _filename = None

    # Content stored as a list of lines
    _content = []

    # Relative position to where the lines were at the beginning
    _deltas = []

    # keep track what is the next original line
    _next_original_delta_index = []

    _cursor = None  # 0-indexed pointer to current line
    _original_num_lines = None

    # Indexation managers
    _ind_level = 0
    _ind_string = "  "

    def __init__(self, filename):
        self._filename = filename

        # If file does not exist create an empty file
        if not os.path.isfile(filename):
            open(filename, 'a').close()

        self.load(filename)

    def load(self, filetocopy):
        '''
        Populates rewrite buffer with filetocopy contents. It destroys any
        previous content in the buffer.

        :param filetocopy: Path to file that will be copied into the buffer.
        '''

        with open(filetocopy, 'r') as fobj:
            self._content = fobj.read().splitlines()
        self._cursor = 1
        self._original_num_lines = len(self._content)
        self._deltas = [0] * self._original_num_lines
        self._next_original_delta_index = \
            list(range(0, self._original_num_lines))

    def get_line(self):
        ''' Returns current cursor line.'''
        return self._cursor

    def get_content(self):
        ''' Returns cursor line content.'''
        return self._content[self._cursor - 1]  # cursor is 1-indexed

    def goto_line(self, number):
        '''
        Move the cursor to provided line number.

        :param number: Line number
        '''
        if (number > len(self._content) or number < 1):
            raise IndexError("File only has " +
                             str(len(self._content)) + " lines.")
        self._cursor = number  # 0-indexing

    def goto_original_line(self, number):
        '''
        Move the cursor to the new possitional of the original line
        number provided.

        :param number: Line number in original file.
        '''
        if (number > self._original_num_lines or number < 1):
            raise IndexError("Original file only had " +
                             str(self._original_num_lines)+" lines.")
        self._cursor = number + self._deltas[number - 1]

    def insert(self, string):
        '''
        Insert string into the cursor position.

        :param str string: String to insert.
        '''
        # Update content
        self._content.insert(self._cursor - 1,
                             (self._ind_string * self._ind_level) + string)

        # Update deltas
        if self._original_num_lines > 0:
            for i in range(self._next_original_delta_index[self._cursor - 1],
                           self._original_num_lines):
                self._deltas[i] = self._deltas[i] + 1

            no_index = self._next_original_delta_index[self._cursor - 1]

            self._next_original_delta_index.insert(self._cursor - 1, no_index)

        # for i in range(no_index, len(self._content)):
        #    self.next_original_delta_index[i] = \
        #            self.next_original_delta_index[i] + 1

        # Update Cursor
        self._cursor = self._cursor + 1

    def insertpl(self, string):
        '''
        Insert string at the end of the previous line and don't update the
        cursor.

        :param str string: String to insert.
        '''
        self._content[self._cursor - 2] = (self._content[self._cursor - 2] +
                                           " " + string)

    def insertstr(self, string):
        '''
        Insert string inside a C style literal like: "<string>\\n"

        :param str string: String to insert.
        '''
        self.insert("\"" + string.replace('\\', '\\\\').replace('\"', '\\"') + "\\n\"")

    def insertstr_nolb(self, string):
        '''
        Insert string inside a C style literal without a line break: "<string>"

        :param str string: String to insert.
        '''
        self.insert("\"" + string + "\"")

    def delete(self):
        '''
        Delete current cursor line contents.
        '''
        self._content.pop(self._cursor - 1)

        # Update deltas
        if self._original_num_lines > 0:
            for i in range(self._next_original_delta_index[self._cursor],
                           self._original_num_lines):
                self._deltas[i] = self._deltas[i] - 1

            # no_index = self._next_original_delta_index[self._cursor - 1]
            self._next_original_delta_index.pop(self._cursor - 1)

        # when cursor was last line, decrease it
        self._cursor = min(self._cursor, len(self._content))

    def replace(self, string):
        '''
        Replace contents from the cursor line with the new provided string.

        :param str string: String to insert.
        '''
        self._content[self._cursor - 1] = (self._ind_string *
                                           self._ind_level) + string
        self._cursor = self._cursor + 1

    def comment(self):
        ''' Prefix cursor line with C-style comment symbol. '''
        self.replace("//" + self._content[self._cursor - 1])

    def increase_indexation(self):
        ''' Increase indentation level. '''
        self._ind_level = self._ind_level + 1

    def decrease_indexation(self):
        ''' Decrease indentation level. '''
        self._ind_level = max(self._ind_level - 1, 0)

    def print_range(self, start, end):
        '''
        Print content from provided start to end line.

        :param start: Start line.
        :param end: End line.
        '''
        print("--- Buffer from line " + str(start) + " to " + str(end) +
              " ---")
        for line in range(start, end + 1):
            if line == self._cursor:
                print("->" + str(line) + ": " + self._content[line - 1])
            else:
                print("  " + str(line) + ": " + self._content[line - 1])
        print("--- End range ---")

    def printall(self):
        ''' Print full buffer.'''
        self.print_range(1, len(self._content))

    def save(self):
        ''' Save buffer contents to file. '''
        with open(self._filename, 'w') as fobj:
            fobj.write("\n".join(self._content))
