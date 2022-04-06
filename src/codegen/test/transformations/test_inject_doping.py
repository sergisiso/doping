# pylint: disable=no-self-use, protected-access

''' Py.test tests for the InjectDoping transformation class as
implemented in transformations/inject_doping.py '''

import os
import re
import pytest
from codegen.transformations import InjectDoping


class TestInjectDoping:
    ''' Test the InjectDoping transformation class '''

    @pytest.fixture
    def input_file(self, tmpdir):
        ''' Create a temporary file called test.txt with 3 lines '''
        filename = os.path.join(str(tmpdir), "input.c")
        return filename

    @pytest.fixture
    def output_file(self, tmpdir):
        ''' Create a temporary file called test.txt with 3 lines '''
        filename = os.path.join(str(tmpdir), "output.c")
        return filename

    @staticmethod
    def _filter_dyn_code(source):
        ''' Find the dynamic optimized source code. It extracts it from the
        ".source= "<source code>" expression in the given source. It expects
        only one region of dynamically optimized code. '''
        dynopt_code = ""
        lines = source.split("\n")

        # We know the exact match of the line before the dynopt code
        start = lines.index("    .source = \"\\n\"") + 1
        for line in lines[start:]:
            # We know how the first line after the dynopt starts
            if line.startswith("    .compiler_command ="):
                break

            # Reconstruct string-line (remove initial " and final \n")
            strline = line[1:-1].replace('\\\\', '\\').replace('\\"', '\"')
            if strline.endswith('\\n'):
                strline = strline[:-2]
            dynopt_code += strline + '\n'

        return dynopt_code[:-5]  # Remove the last characters not part of the source

    def test_source_with_no_candidate(self, input_file, output_file):
        ''' Test a helloworld input file with no loop'''

        with open(input_file, "w") as source:
            source.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n
                \n
                int main(){\n
                    printf("Hello World");\n
                    return 0;\n
                }\n
                '''
            )

        # Initialize
        doping_trans = InjectDoping(input_file, output_file)
        assert not doping_trans._is_cpp

        # Apply transformation
        doping_trans.apply()

    def test_loop_with_no_candidate(self, input_file, output_file, capsys):
        ''' Test a input file with a loop but no dynamic optimization opportunity '''

        with open(input_file, "w") as source:
            source.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n
                \n
                int main(){\n
                    for(int i=0; i<10; i++){
                        printf("Hello World");\n
                    }
                    return 0;\n
                }\n
                '''
            )

        # Initialize
        doping_trans = InjectDoping(input_file, output_file)
        assert not doping_trans._is_cpp

        # Apply transformation
        # import pdb; pdb.set_trace()

        doping_trans.apply()
        captured = capsys.readouterr()
        assert re.search("Analyzing loop at .*input.c', line 10, column 21>", captured.out)
        assert "> No dynamic optimization applied" in captured.out

    def test_loop_with_a_true_candidate(self, input_file, output_file, capsys, compiler):
        ''' Test a loop containing a runtime invariant '''

        with open(input_file, "w") as source:
            source.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n
                \n
                int main(){\n
                    int constvar = 3;
                    for(int i=0; i<10; i++){
                        printf("The const is %d.\\n", constvar);\n
                    }
                    return 0;\n
                }\n
                '''
            )

        # Initialize
        doping_trans = InjectDoping(input_file, output_file, compiler.flags)
        assert not doping_trans._is_cpp

        # Apply transformation
        doping_trans.apply()
        captured = capsys.readouterr()
        print(captured.out)
        regexpr = (
            "Analyzing loop at .*input.c', line 11, column 21>\n"
            + re.escape(
                "    Local vars:\n"
                "        i (int)\n"
                "    Arrays/Pointers:\n"
                "    Scalar writes:\n"
                "    Vars for delayed evaluation:\n"
                "        constvar (int)\n"
                "    Number of function calls: 1\n"))
        assert re.search(regexpr, captured.out)
        assert "> Creating dynamically optimized version of the loop." in captured.out

        with open(output_file, "r") as source:
            output_source = source.read()

        print(output_source)
        # It adds a doping.h include
        assert output_source.startswith('#include "doping.h"')

        # It comments out the original code
        regexpr = (
            re.escape("//  ---- CODE TRANSFORMED BY doping ----\n") +
            "//  ---- Old version from <SourceLocation file .* line 11, column 21>"
            "----\n" +
            re.escape(
                "//                    for(int i=0; i<10; i++){\n"
                "//                        printf(\"The const is %d.\\n\", constvar);\n"
                "//\n"
                "//                    }\n"
            )
        )
        assert re.search(regexpr, output_source)

        # It creates a new scope and initializes dopingRuntimeVal with the invariant
        regexpr = (
            re.escape(
                "//  ---- New version: ----\n"
                "{  // start a doping scope\n"
                "char dopingRuntimeVal_1[100];\n"
                "sprintf(dopingRuntimeVal_1,  \"constvar:%d\",  constvar);"
            )
        )
        assert re.search(regexpr, output_source)

        # Created the dopinginfo object (exclude source checking in this test)
        regexpr = (
            re.escape(
                "dopinginfo info1 = {\n"
                "    .iteration_start = 0,\n"
                "    .iteration_space = (10 - 1),\n"
            ) + "    .source = .*\n"
        )
        assert re.search(regexpr, output_source)
        regexpr = (
            re.escape(
                "    .compiler_command = \"" + compiler.flags + "\",\n"
                "    .parameters = dopingRuntimeVal_1,\n"
            )
        )
        assert re.search(regexpr, output_source)

        # Write a version of the original loop inside a dopingRuntime while expression
        # and the initialization done before the while loop.
        # print(output_source.split(','))
        regexpr = (
            re.escape(
                "int i = 0;\n"
                "while(dopingRuntime(i, i < 10, &info1, NULL )){\n"
                "  \n"
                "  // Unmodified loop\n"
                "  for(; (i < 10  ); i ++) {\n"
            )
        )
        assert re.search(regexpr, output_source)
        regexpr = (
            re.escape(
                "}\n"
                "} //end while loop\n"
                "} //close doping scope\n"
            )
        )
        assert re.search(regexpr, output_source)

        # Compile and run the output_file
        assert compiler.compile(output_file)
        assert compiler.run(match="Rendering template, compilation and linking took:",
                            verbosity=2)

    @pytest.mark.xfail(reason="only one pragma line is copied for now")
    def test_loop_with_pragmas(self, input_file, output_file, capsys, compiler):
        ''' Test a loop containing a runtime invariant and OpenMP pragmas '''

        with open(input_file, "w") as source:
            source.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n
                \n
                int main(){\n
                    int constvar = 3;
                    # pragma omp parallel
                    # pragma omp for
                    # pragma omp simd
                    for(int i=0; i<10; i++){
                        #pragma omp critical
                        printf("The const is %d.\\n", constvar);\n
                    }
                    return 0;\n
                }\n
                '''
            )

        # Initialize
        doping_trans = InjectDoping(input_file, output_file, compiler.flags)

        # Apply transformation
        doping_trans.apply()
        captured = capsys.readouterr()
        print(captured.out)
        regexpr = (
            "Analyzing loop at .*input.c', line 14, column 21>\n"
            + re.escape(
                "    Local vars:\n"
                "        i (int)\n"
                "    Arrays/Pointers:\n"
                "    Scalar writes:\n"
                "    Vars for delayed evaluation:\n"
                "        constvar (int)\n"
                "    Number of function calls: 1\n"
                "    > Creating dynamically optimized version of the loop.\n"))
        assert re.search(regexpr, captured.out)
        assert "> Creating dynamically optimized version of the loop." in captured.out

        with open(output_file, "r") as source:
            output_source = source.read()

        print(output_source)

        # It comments out the original code including the pragmas
        regexpr = (
            re.escape(
                "//                    # pragma omp parallel\n"
                "//                    # pragma omp for\n"
                "//                    # pragma omp simd\n"
                "//  ---- CODE TRANSFORMED BY doping ----\n") +
            "//  ---- Old version from <SourceLocation file .* line 11, column 21>"
            "----\n" +
            re.escape(
                "//                    for(int i=0; i<10; i++){\n"
                "//                        # pragma omp critical\n"
                "//                        printf(\"The const is %d.\\n\", constvar);\n"
                "//\n"
                "//                    }\n"
            )
        )
        assert re.search(regexpr, output_source)

    def test_dynamic_code_simple_loop(self, input_file, output_file, capsys, compiler):
        ''' Test a loop containing a runtime invariant '''

        with open(input_file, "w") as source:
            source.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n
                \n
                int main(){\n
                    int constvar = 3;
                    for(int i=0; i<10; i++){
                        printf("The const is %d.\\n", constvar);\n
                    }
                    return 0;\n
                }\n
                '''
            )

        # Initialize
        doping_trans = InjectDoping(input_file, output_file, compiler.flags)
        doping_trans.apply()
        captured = capsys.readouterr()
        print(captured.out)

        with open(output_file, "r") as source:
            output_source = source.read()

        dynopt_code = self._filter_dyn_code(output_source)

        print(dynopt_code)

        # Check it imports stdarg needed for the variadic list
        assert dynopt_code.startswith('#include <stdarg.h>')

        # Check it contains the expected function signature
        assert ("void function(\nint dopingCurrentIteration,\n"
                "va_list args){\n" in dynopt_code)

        # Check the runtime invariant is initialized with a DOPING substitution as expected
        assert "const int constvar = /*<DOPING constvar >*/;" in dynopt_code

    def test_dynamic_code_with_preprocessor(self, input_file, output_file, capsys, compiler):
        ''' Test a loop containing a runtime invariant and preprocessor statements outside
        the dynamically compiled region.'''

        with open(input_file, "w") as source:
            source.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n
                #ifndef VAR\n
                #define VAR myvariable\n
                #endif\n
                \n
                int main(){\n
                    int constvar = 3;\n
                    #define MYOTHERVAR mysecondvariable\n
                    for(int i=0; i<10; i++){\n
                        printf("The const is %d.\\n", constvar);\n
                    }\n
                    #define LOOPDONE\n
                    return 0;\n
                }\n
                #define LASTDEFINE\n
                '''
            )

        # Initialize
        doping_trans = InjectDoping(input_file, output_file, compiler.flags)
        doping_trans.apply()
        captured = capsys.readouterr()
        print(captured.out)

        with open(output_file, "r") as source:
            output_source = source.read()

        dynopt_code = self._filter_dyn_code(output_source)

        print(dynopt_code)

        # Check it imports stdarg is still before any preprocessor expression
        assert dynopt_code.startswith('#include <stdarg.h>')

        # Check that the preprocessor expressions before the loop are now before
        # the 'function' (but not the expressions after)
        dynopt_start = dynopt_code.index("void function(")
        assert "#include<stdio.h>" in dynopt_code[:dynopt_start]
        assert "#ifndef VAR" in dynopt_code[:dynopt_start]
        assert "#define VAR myvariable" in dynopt_code[:dynopt_start]
        assert "#endif" in dynopt_code[:dynopt_start]
        assert "#define MYOTHERVAR mysecondvariable" in dynopt_code[:dynopt_start]
        assert "#define LOOPDONE" not in dynopt_code[:dynopt_start]
        assert "#define LASTDEFINE" not in dynopt_code[:dynopt_start]

        # Check that the preprocessor expressions after the loop are now after
        # the 'function' (but not the expressions before)
        assert "#include<stdio.h>" not in dynopt_code[dynopt_start:]
        assert "#ifndef VAR" not in dynopt_code[dynopt_start:]
        assert "#define VAR myvariable" not in dynopt_code[dynopt_start:]
        assert "#endif" not in dynopt_code[dynopt_start:]
        assert "#define MYOTHERVAR mysecondvariable" not in dynopt_code[dynopt_start:]
        assert "#define LOOPDONE" in dynopt_code[dynopt_start:]
        assert "#define LASTDEFINE" in dynopt_code[dynopt_start:]

    def test_dynamic_code_function_calls(self, input_file, output_file, capsys, compiler):
        ''' Test a loop containing a runtime invariant and a function call inside the
        dynamically compiled region.'''

        with open(input_file, "w") as source:
            source.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n

                int add(int a, int b){\n
                    return a + b;\n
                }\n

                int main(){\n
                    int constvar = 3;
                    for(int i=0; i<10; i++){
                        int sum = add(constvar, 3);
                        printf("The const is %d.\\n", sum);\n
                    }
                    return 0;\n
                }\n
                '''
            )

        # Initialize
        doping_trans = InjectDoping(input_file, output_file, compiler.flags)
        doping_trans.apply()
        captured = capsys.readouterr()
        print(captured.out)

        with open(output_file, "r") as source:
            output_source = source.read()

        # It must identify 2 functions,
        assert "Number of function calls: 2" in captured.out
        # which shouldn't stop the dynamic optimization
        assert "> Creating dynamically optimized version of the loop." in captured.out

        return
        # the 'add' function source is found in the file
        assert "- Function 'add' definition found" in captured.out
        # while the 'printf' function is not found
        assert "- Declaration of function 'printf' " in captured.out
        assert "Assuming it is defined in imported headers." in captured.out

        # The generated code must include the headers and the found functions
        dynopt_code = self._filter_dyn_code(output_source)
        print(dynopt_code)
        assert "#include<stdio.h>" in dynopt_code
        assert "int add(int a, int b){" in dynopt_code
        assert compiler.compile(output_file)
        assert compiler.run(match="Rendering template, compilation and linking took:",
                            verbosity=1)

    def test_dynamic_code_with_global(self, input_file, output_file, capsys, compiler):
        ''' Test a loop containing a runtime invariant and access to global variables '''

        with open(input_file, "w") as source:
            source.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n
                \n
                #define TYPE float\n

                int intglobal = 2;
                TYPE typeglobal = 4;

                int main(){\n
                    int constvar = 3;
                    TYPE array[100];
                    for(int i=0; i<10; i++){
                        intglobal = intglobal + constvar;
                        printf("The const is %d, array is %f.\\n", intglobal, typeglobal);\n
                    }
                    return 0;\n
                }\n
                '''
            )

        # Initialize
        doping_trans = InjectDoping(input_file, output_file, compiler.flags)
        doping_trans.apply()
        captured = capsys.readouterr()
        print(captured.out)

        with open(output_file, "r") as source:
            output_source = source.read()

        print(output_source)

        dynopt_code = self._filter_dyn_code(output_source)

        print(dynopt_code)
        # TODO: Define what I expect
        assert compiler.compile(output_file)
        assert compiler.run(match="Rendering template, compilation and linking took:",
                            verbosity=2)

    def test_dynamic_code_with_structs(self, input_file, output_file, capsys, compiler):
        ''' Test a loop containing a runtime invariant and access to global variables '''

        with open(input_file, "w") as source:
            source.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n
                \n
                struct point {
                    int x;
                    int y;
                };

                int main(){\n
                    struct point p = {1,2};
                    int constvar = 3;
                    for(int i=0; i<10; i++){
                        p.x = 3;
                        int result = p.x + constvar;
                        printf("The result is %d\\n", result);\n
                    }
                    return 0;\n
                }\n
                '''
            )

        # Initialize
        doping_trans = InjectDoping(input_file, output_file, compiler.flags)
        doping_trans.apply()
        captured = capsys.readouterr()
        print(captured.out)

        with open(output_file, "r") as source:
            output_source = source.read()

        print(output_source)

        dynopt_code = self._filter_dyn_code(output_source)

        print(dynopt_code)
        # TODO: Define what I expect
        assert compiler.compile(output_file)
        assert compiler.run(match="Rendering template, compilation and linking took:",
                           verbosity=2)

    def test_nested_dynamic_code(self, input_file, output_file, capsys, compiler):
        ''' Test a loop containing a runtime invariant and a function call that
        have another loop with runtime invariants.'''

        with open(input_file, "w") as source:
            source.write(
                '''
                /* Hello World program */\n
                #include<stdio.h>\n
                \n
                #define TYPE float\n

                int ap_n0 = 0;
                int bp_n4 = 4;


                TYPE test(TYPE * A){\n
                    TYPE s = (TYPE)ap_n0;\n
                    for (int i = 0; i < bp_n4; i++) s += A[i];\n
                    return s;\n
                }\n

                int main(){\n
                    int constvar = 3;
                    TYPE array[100];
                    for(int i=0; i<10; i++){
                        TYPE sum = test(array);
                        printf("The const is %d, array is %f.\\n", constvar, sum);\n
                    }
                    return 0;\n
                }\n
                '''
            )

        # Initialize
        doping_trans = InjectDoping(input_file, output_file, compiler.flags)
        doping_trans.apply()
        captured = capsys.readouterr()
        print(captured.out)

        with open(output_file, "r") as source:
            output_source = source.read()

        print(output_source)

        dynopt_code = self._filter_dyn_code(output_source)

        print(dynopt_code)
        # TODO: Define what I expect
        assert compiler.compile(output_file)
        assert compiler.run(match="Rendering template, compilation and linking took:",
                            verbosity=2)
