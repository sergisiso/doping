#!/bin/env python3

import os
import argparse
from subprocess import call

from codegen import codegen

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


if __name__ == "__main__":
    main()


