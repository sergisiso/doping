
import sys
import clang.cindex


class Rewriter:

    filename = None
    content = []
    cursor = 0

    def __init__(self, filename):
        self.filename = filename
        with open(filename,'w+') as f:
            self.content = f.read().splitlines()
        self.cursor = 0

    def copy(self, filetocopy):
        with open(filetocopy,'r') as f:
            self.content = f.read().splitlines()
        self.cursor = 0

    def goto_line(self, number):
        self.cursor = number - 1 # 0-indexing

    def insert(self, string):
        self.content.insert(self.cursor, string)
        self.cursor = self.cursor + 1
    
    def replace(self, string):
        self.content[self.cursor] = string
        self.cursor = self.cursor + 1
 
    def comment(self):
        self.content[self.cursor] = "//" + self.content[self.cursor]
        self.cursor = self.cursor + 1


    def print_range(self, start, end):
        for line in range(start,end):
            print( str(line+1)+ ": " + self.content[line])

    def printall(self):
        self.print_range(0,len(self.content))

    def save(self):
        with open(self.filename,'w') as f:
            f.write("\n".join(self.content))

class AST:
    
    treeroot = None
    filename = None
    originalcode = None

    def __init__(self, input):
        self.create_AST(input)
        self.filename = input
        self.originalcode = "aaa"

    def create_AST(self, input):
        index = clang.cindex.Index.create()
        self.treeroot = index.parse(input)

    def _is_from_file(self, node):
        return node.location.file.name == self.filename
    
    def str_position(self, node):
        return "["+ node.location.file.name + ", line:" + str(node.location.line) \
                + ", col:" + str(node.location.column) + "]"

    def node_to_str(self, node, recursion_level = 0):
            childrenstr = []
            if recursion_level < 5:
                for child in filter(self._is_from_file,node.get_children()) :
                    childrenstr.append(self.node_to_str(child,recursion_level+1))
            text = node.spelling or node.displayname
            kind = str(node.kind)[str(node.kind).index('.')+1:]
            return  ("    " * recursion_level) + kind + " " + text + "\n" + "\n".join(childrenstr)

    def find_loops(self):
        looplist = self._find(self.treeroot.cursor, clang.cindex.CursorKind.FOR_STMT)
        for node in filter(self._is_from_file,looplist):
            print("FOR Loop Found at " + self.str_position(node) )
        return looplist

    def generate_taskgraph(self,file):
        node = filter(self._is_from_file,self.find_loops())[0]
        print( "-> Generating taskgraph for loop at " + self.str_position(node))
        print(self.node_to_str(node))
        print(node.extent.end.line)
        
        file.goto_line(node.extent.start.line)
        file.insert("//  --------- CODE TRANSFORMED BY JAKE ----------")
        file.insert("//  --------- Old version: ----------")
        # Comment old code
        for i in range((node.extent.end.line - node.extent.start.line)+1):
            file.comment()

        file.insert("//  --------- TG version: ----------")
        #file.insert("std::cout << \"Creating TaskGraph ...\" << std::endl;")
        tg_id = "tg0"
        tg_type = "tgtype"
        tg_input = ["MatrixType","MatrixType","MatrixType"]
        file.insert(" typedef SCALARTYPE MatrixType[MATRIXSIZE][MATRIXSIZE];")
        file.insert("typedef tg::TaskGraph<void,"+",".join(tg_input)+"> "+tg_type+";")
        file.insert(tg_type+" "+tg_id+";")
        # macro taskgraph(type, name, parameters)
        file.insert("taskgraph("+tg_type+", "+tg_id+", tuple3(a,b,c) ) {")
        file.insert("tVar ( int, x );")
        file.insert("tVar ( int, y );")
        file.insert("tVar ( int, z );")

        self.libclang_to_tg(node,file)

        file.insert("}")
        #file.insert("std::cout << \"Compiling...\" << std::endl;")
        file.insert(tg_id+".compile( tg::GCC);" )
        #file.insert("std::cout << \"Executing...\" << std::endl;")
        file.insert(tg_id+".execute(a,b,c);")

        file.goto_line(1)
        file.insert("#include <TaskGraph>")
        file.goto_line(5)
        file.insert("using namespace tg;")

        file.printall()

    def libclang_to_tg(self, node, file):

        kind = str(node.kind)[str(node.kind).index('.')+1:]
        #print([x.spelling for x in list(node.get_tokens())])
        if node.kind == clang.cindex.CursorKind.FOR_STMT:
            #FOR_STMT structure: for(child0 ; child1 ; child2){ child3 }
            child = [ c for c in node.get_children()]
            s0 = [x.spelling for x in child[0].get_tokens()]
            s1 = [x.spelling for x in child[1].get_tokens()]
            s2 = [x.spelling for x in child[2].get_tokens()]
            # s0 give one token more than necessary, is that a libclang bug?
            # file.insert("for( "+" ".join(s0[:-1])+" ".join(s1)+" ".join(s2) +"{")
            file.insert("tFor( "+str(list(child[0].get_children())[0].spelling)+", 0 , MATRIXSIZE - 1 ){")
            self.libclang_to_tg(child[3],file)
            file.insert("}")
        elif node.kind == clang.cindex.CursorKind.COMPOUND_STMT:
            # What exaclty is COMPOUND_STMT? I only see one STMT
            for c in node.get_children():
                self.libclang_to_tg(c,file)
        else:
            file.insert(" ".join([x.spelling for x in node.get_tokens()]))



    def _find(self, node, type):
        listofmatches = []

        try:
            if (node.kind == type): listofmatches.append(node)
        except ValueError:
            pass
         
        # Recurse for children of this node
        for c in node.get_children():
            listofmatches.extend(self._find(c,type))

        return listofmatches


    def __str__(self):
        return "AST:\n" + self.node_to_str(self.treeroot.cursor)



def generate_new_code(input, output):
    finput = open(input, 'r')
    foutput = open(output, 'w')
    foutput.write(finput.read())

def generate_new_code_test(input, output):

    # make a copy of the file to the output location
    file = Rewriter(output)
    file.copy(input)

    #parse code and generate ast tree
    ast = AST(input)

    #rewrite file with taskgraph code 
    ast.generate_taskgraph(file)

    #save file
    file.save()

if __name__ == "__main__":
    generate_new_code_test(sys.argv[1], sys.argv[2])
