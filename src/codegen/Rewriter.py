
class Rewriter:

    filename = None
    # Content stored as a list of lines
    content = []
    # 0-indexed pointer to line
    cursor = 0
    # Indexation managers
    ind_level = 0
    ind_string = "  "

    def __init__(self, filename):
        self.filename = filename
        with open(filename,'r') as f:
            self.content = f.read().splitlines()
        self.cursor = 0

    def copy(self, filetocopy):
        with open(filetocopy,'r') as f:
            self.content = f.read().splitlines()
        self.cursor = 0

    def goto_line(self, number):
        self.cursor = number - 1 # 0-indexing

    def insert(self, string):
        self.content.insert(self.cursor, (self.ind_string * self.ind_level) + string)
        self.cursor = self.cursor + 1

    def delete(self):
        self.content.pop(self.cursor)
        # when cursor was last line, decrease it
        self.cursor = min(self.cursor, max(len(content)-1,0)) 

    def insertpl(self, string):
        if self.cursor <= 0: raise IndexError("Cannot append in previous line when cursor is 0")
        self.cursor = self.cursor - 1
        self.append(string)

    def append(self, string):
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

