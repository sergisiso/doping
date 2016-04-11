
import sys
import clang.cindex

import asciitree

def generate_new_code(input, output):
    finput = open(input, 'r')
    foutput = open(output, 'w')
    foutput.write(finput.read())

def find_typerefs(node, typename):
    """ Find all references to the type named 'typename'
    """
    #print('kind: %s, spelling: %s [line=%s, col=%s]' % (node.kind, node.spelling, node.location.line, node.location.column))
    if (node.kind == clang.cindex.CursorKind.FOR_STMT):
        print('For statement found at [line=%s, col=%s]' % (node.location.line, node.location.column))

    # Recurse for children of this node
    for c in node.get_children():
        find_typerefs(c, typename)

def node_children(node):
    #return (c for c in node.get_children() if c.location.file.name == sys.argv[1])
    return (c for c in node.get_children() if true)

def print_node(node):
    text = node.spelling or node.displayname
    kind = str(node.kind)[str(node.kind).index('.')+1:]
    return '{} {}'.format(kind, text)

def generate_new_code_test(input, output):
    finput = open(input, 'r')
    index = clang.cindex.Index.create()
    translation_unit = index.parse(input)
    print(asciitree.draw_tree(translation_unit.cursor, node_children, print_node))
    #find_typerefs(tu.cursor, "Person")

if __name__ == "__main__":
    generate_new_code_test(sys.argv[1], sys.argv[2])
