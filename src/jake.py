#!/bin/env python

import os
import sys
import argparse
from subprocess import call
from codegen.Rewriter import Rewriter
from codegen.CodeTransformation import LoopProfiling, GenerateTaskGraph

ext = ['.cpp', '.c', '.cc']

def main():
    
    # Parse input arguments
    parser = argparse.ArgumentParser(description=" ")
    parser.add_argument('compiler_command', nargs="+", help='the command used by the compiler')
    args = parser.parse_args()
    

    # Source to Source transformation of C/C++ files
    print("Replacing C/C++ files:")
    c_files = [x for x in args.compiler_command if x.endswith(tuple(ext))]
    new_compiler_command = args.compiler_command

    for file in c_files:
        index = args.compiler_command.index(file)
        filename, file_extension = os.path.splitext(file)
        newfile = filename + ".jake" + file_extension
        codegen.generate_new_code(file,newfile)
        print(" * Code generated for", file, " file")
        new_compiler_command[index] = newfile
        

    # Compile the generated code
    print("Compiling code using: ", ' '.join(new_compiler_command))
    call(list(new_compiler_command), shell=False)

def generate_new_code_test(input, output):

    # make a copy of the file to the output location
    file = Rewriter(output)
    file.copy(input)
    file.save()

    # Create and apply transformations
    trans1 = LoopProfiling(output)
    trans1.apply()

    #trans2 = GenerateTaskGraph(output)
    #trans2.apply()


if __name__ == "__main__":
    generate_new_code_test(sys.argv[1], sys.argv[2])
    #main()


