
def generate_new_code(input, output):
    finput = open(input, 'r')
    foutput = open(output, 'w')
    
    foutput.write(finput.read())

