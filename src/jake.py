#!/usr/bin/env python

import os
import sys
import argparse
from shutil import copyfile
from subprocess import call
from codegen.Rewriter import Rewriter
from codegen.CodeTransformations import InjectJake, GenerateTaskGraph

ext = ['.cpp', '.c', '.cc']

def main():

    # Initial checks
    if not 'JAKEROOT' in os.environ:
        print "Error: Environment variable JAKEROOT not defined!"
        exit(-1)
    
    jakeruntimepath = os.path.join(os.environ['JAKEROOT'],"src/runtime/JakeRuntime.o")

    if not os.path.isfile( jakeruntimepath ):
        print "Error: Can't find Jake Runtime object file. Is Jake properly compiled?"
        exit(-1)

    # Parse input arguments
    parser = argparse.ArgumentParser(description=" ")
    parser.add_argument('compiler_command', nargs="+", help='the command used by the compiler')
    args = parser.parse_args()
    
    # Find C/C++ files in the input commnad
    c_files = [x for x in args.compiler_command if x.endswith(tuple(ext))]

    # Link dl and JakeRuntime libraries
    new_compiler_command = args.compiler_command
    new_compiler_command.append("-ldl")
    new_compiler_command.append(jakeruntimepath)

    # Source to Source transformation of C/C++ files
    print("Optimizing C/C++ files:")
    for file in c_files:
        index = args.compiler_command.index(file)
        filename, file_extension = os.path.splitext(file)
        newfile = filename + ".jake" + file_extension
        copyfile(file, newfile)
        print("- Generating code for " + file + " ->" + newfile)
        transformation = InjectJake.InjectJake(newfile)
        transformation.apply()
        new_compiler_command[index] = newfile
        
    # Compile the generated code
    print("Compiling code:")
    print(' '.join(new_compiler_command))
    call(list(new_compiler_command), shell=False)

if __name__ == "__main__":
    main()


