import os

class Rewriter:

    ''' This class implements a 're-write buffer' as a list of lines
    and allows to insert/delete/replace lines. It also keep track of the position
    of the original lines, this allows to place the cursor using the current line
    numbers or the original line numbers. It is useful for making modifications
    in multiple locations of the buffer when the user only has references to the
    original line numbers (like the pre-parsed AST tree)'''


    filename = None
    content = [] # Content stored as a list of lines

    deltas = [] # Relative position to where the lines were at the beginning
    next_original_delta_index = [] # keep track what is the next original line

    cursor = None # 0-indexed pointer to current line
    original_num_lines = None

    # Indexation managers
    ind_level = 0
    ind_string = "  "

    def __init__(self, filename):
        self.filename = filename

        # If file does not exist create an empty file
        if not os.path.isfile(filename):
            open(filename,'a').close()

        self.load(filename)

    def load(self, filetocopy):
        with open(filetocopy,'r') as f:
            self.content = f.read().splitlines()
        self.cursor = 1
        self.original_num_lines = len(self.content)
        self.deltas = [0]  * self.original_num_lines
        self.next_original_delta_index = list(range(0,self.original_num_lines))

    def get_line(self):
        return self.cursor

    def get_content(self):
        return self.content[self.cursor - 1] # cursor is 1-indexed

    def goto_line(self, number):
        if (number > len(self.content) or number < 1):
            raise IndexError("File only has "+str(len(self.content))+" lines.")
        self.cursor = number # 0-indexing

    def goto_original_line(self, number):
        if (number > self.original_num_lines or number < 1):
            raise IndexError("Original file only had " + \
                    str(self. original_num_lines)+" lines.")
        self.cursor = number + self.deltas[number - 1]

    def insert(self, string):
        # Update content
        self.content.insert(self.cursor - 1, \
                (self.ind_string * self.ind_level) + string)

        # Update deltas
        for i in range(self.next_original_delta_index[self.cursor - 1] \
                , self.original_num_lines):
            self.deltas[i] = self.deltas[i] + 1

        no_index = self.next_original_delta_index[self.cursor - 1]

        self.next_original_delta_index.insert(self.cursor - 1, no_index)

        #for i in range(no_index, len(self.content)):
        #    self.next_original_delta_index[i] = \
        #            self.next_original_delta_index[i] + 1


        # Update Cursor
        self.cursor = self.cursor + 1


    def delete(self):
        self.content.pop(self.cursor - 1)

        # Update deltas
        for i in range(self.next_original_delta_index[self.cursor] \
                , self.original_num_lines):
            self.deltas[i] = self.deltas[i] - 1

        no_index = self.next_original_delta_index[self.cursor - 1]
        self.next_original_delta_index.pop(self.cursor - 1)

        # when cursor was last line, decrease it
        self.cursor = min(self.cursor, len(self.content)) 

    def insertpl(self, string):
        self.content[self.cursor - 1] = self.content[self.cursor - 1] \
                + " " + string
    
    def replace(self, string):
        self.content[self.cursor - 1] = (self.ind_string * self.ind_level)\
                + string
        self.cursor = self.cursor + 1
 
    def comment(self):
        self.replace("//" + self.content[self.cursor])

    def increase_indexation(self):
        self.ind_level = self.ind_level + 1

    def decrease_indexation(self):
        self.ind_level = max(self.ind_level - 1, 0)

    def print_range(self, start, end):
        for line in range(start,end):
            print( str(line+1)+ ": " + self.content[line])

    def printall(self):
        self.print_range(0,len(self.content))

    def save(self):
        with open(self.filename,'w') as f:
            f.write("\n".join(self.content))

