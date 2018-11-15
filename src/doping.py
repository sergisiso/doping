#!/usr/bin/env python

import os
import sys
import argparse
from shutil import copyfile
from subprocess import call
from codegen.Rewriter import Rewriter
from codegen.CodeTransformations import InjectDoping

ext = ['.cpp', '.c', '.cc']

def main():

    # Initial Environment checks
    if not 'DOPING_ROOT' in os.environ:
        print "Error: Environment variable DOPING_ROOT not defined!"
        exit(-1)
    
    dopingruntimepath = os.path.join(os.environ['DOPING_ROOT'],"bin/dopingRuntime.o")

    if not os.path.isfile( dopingruntimepath ):
        print "Error: Can't find doping Runtime object file. Is doping properly compiled?"
        exit(-1)

    # Parse input arguments
    parser = argparse.ArgumentParser(description=" ")
    parser.add_argument('--verbosity', type=int, default='1', choices=[0,1,2,3,4], \
            help='verbosity level: 0 - non-verbose, 1 - Errors, 2 - Warnings, 3 - Messages, 4 - Debug (default = 1)' )
    parser.add_argument('compiler_command', nargs="+", help='the command used by the compiler')
    args = parser.parse_args()
    
    # Find C/C++ files in the input commnad
    c_files = [x for x in args.compiler_command if x.endswith(tuple(ext))]

    # Link dl and dopingRuntime libraries (order is important!)
    new_compiler_command = args.compiler_command
    new_compiler_command.append(dopingruntimepath)
    new_compiler_command.append("-ldl")

    # Probably will break with more complex examples
    flags =  ' '.join(filter( lambda x: x[0] == '-' and not x == '-o' ,args.compiler_command)) 
    flags = str(args.compiler_command[0]) + " " + flags

    # Source to Source transformation of C/C++ files
    print("Optimizing C/C++ files:")
    for file in c_files:
        index = args.compiler_command.index(file)
        filename, file_extension = os.path.splitext(file)
        newfile = filename + ".doping" + file_extension
        copyfile(file, newfile)
        print("- Generating code for " + file + " ->" + newfile)

        print flags
        transformation = Injectdoping.Injectdoping(newfile, flags, args.verbosity)
        transformation.apply()
        new_compiler_command[index] = newfile
        
    # Compile the generated code
    print("Compiling code:")
    print(' '.join(new_compiler_command))
    ret = call(list(new_compiler_command), shell=False)
    exit(ret)

if __name__ == "__main__":
    main()

