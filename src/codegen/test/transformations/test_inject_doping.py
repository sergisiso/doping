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

    def test_source_with_no_candidate(self, input_file, output_file):
        ''' Test a helloworld input file '''

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


    def test_source_with_a_false_candidate(self, input_file, output_file, capsys):
        ''' Test a helloworld input file '''

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
        #import pdb; pdb.set_trace()

        doping_trans.apply()
        captured = capsys.readouterr()
        assert re.search("Analyzing loop at .*input.c', line 10, column 21>", captured.out)
        assert "> No dynamic optimization applied" in captured.out


    def test_source_with_a_true_candidate(self, input_file, output_file, capsys, compiler):
        ''' Test a helloworld input file '''

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
        #import pdb; pdb.set_trace()

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
            "    Number of function calls: 1\n"
            "    > Creating dynamically optimized version of the loop.\n"))
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
            "----------\n" +
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
                "//  --------- New version: ----------\n"
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
                "    .compiler_command = \"" + compiler.flags +"\",\n"
                "    .parameters = dopingRuntimeVal_1,\n"
            )
        )
        assert re.search(regexpr, output_source)

        # Write a version of the original loop inside a dopingRuntime while expression
        # and the initialization done before the while loop.
        #print(output_source.split(','))
        regexpr = (
            re.escape(
                "int i = 0;\n"
                "while(dopingRuntime(i, i < 10, &info1, NULL )){\n"
                "  \n"
                "  // Unmodified loop\n"
                "  for(; (i < 10  ); i ++) {\n"
                "printf (\"The const is %d.\\n\" ,constvar );\n"
                "\n"
                "}\n"
                "} //end while loop\n"
                "} //close doping scope\n"
            )
        )
        assert re.search(regexpr, output_source)

        # Compile and run the output_file
        assert compiler.compile(output_file)
        assert compiler.run(match="Render template, compilation and linking took:",
                            verbosity=1)
