import os

class Rewriter:

    filename = None
    # Content stored as a list of lines
    content = []
    # Relative position to where the lines were at the beginning
    original_lines_pos = []
    original_num_lines = 0
    # 0-indexed pointer to line
    cursor = 0
    # Indexation managers
    ind_level = 0
    ind_string = "  "

    def __init__(self, filename):
        self.filename = filename

        # If file does not exist create an empty file
        if not os.path.isfile(filename):
            open(filename,'a').close()

        # Read lines and set cursor to 0
        with open(filename,'r') as f:
            self.content = f.read().splitlines()
        self.cursor = 0
        self.original_num_lines = len(self.content)
        self.original_lines_pos = range(self.original_num_lines)

    def copy(self, filetocopy):
        with open(filetocopy,'r') as f:
            self.content = f.read().splitlines()
        self.cursor = 0
        self.original_num_lines = len(self.content)
        self.original_lines_pos = range(self.original_num_lines)

    def get_line(self):
        return self.cursor + 1

    def get_content(self):
        return self.content[self.cursor]

    def goto_line(self, number):
        if (number > len(self.content) or number < 1):
            raise IndexError("File only has "+str(len(self.content))+" lines.")
        self.cursor = number - 1 # 0-indexing

    def goto_original_line(self, number):
        if (number > self.original_num_lines or number < 1):
            raise IndexError("Original file only had " + \
                    str(self. original_num_lines)+" lines.")
            raise Error
        self.cursor = self.original_lines_pos[number - 1]
        #print "Goto org ", number
        #print self.original_lines_pos
        #print self.cursor
        #exit()

    def insert(self, string):
        #print "Insert " , self.cursor
        self.content.insert(self.cursor, (self.ind_string * self.ind_level) + string)

        search = 0
        while ( search < self.original_num_lines and \
                self.cursor > self.original_lines_pos[search]):
            search = search + 1

        #print "found", search
        for i in range(search,self.original_num_lines):
            self.original_lines_pos[i] = self.original_lines_pos[i] + 1
        #print self.original_lines_pos
        self.cursor = self.cursor + 1


    def delete(self):
        self.content.pop(self.cursor)
        # when cursor was last line, decrease it
        self.cursor = min(self.cursor, max(len(content)-1,0)) 
        # FIXME: Update original_lines_pos !!!


    def insertpl(self, string):
        if self.cursor <= 0: raise IndexError("Cannot append" + \
                "in previous line when cursor is 0")
        self.cursor = self.cursor - 1
        self.content[self.cursor] = self.content[self.cursor] + " " + string
        self.cursor = self.cursor + 1
    
    def replace(self, string):
        self.content[self.cursor] = (self.ind_string * self.ind_level) + string
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

