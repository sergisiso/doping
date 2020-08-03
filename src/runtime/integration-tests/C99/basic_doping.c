#include <stdio.h>
#include <dopingRuntime.h>

int main(){

    // Runtime examples with C99 code.

    printf("\nExample 1: Single statement without rendering parameters nor data accesses.\n");
    dopinginfo info = {
        .iteration_start = 0,
        .iteration_space = 1,
        .source = "\n"
            "#include <stdio.h>\n"  
            "int function(){\n"
            "   for(int i=0; i < 1; i++) {\n"
            "       printf(\"Print dynamically compiled statement :)\\n\");\n"
            "   }\n"
            "   return 0;\n"
            "}\n",
        .parameters="",
        .compiler_command="gcc ",
    };

    int current = 0;
    int end = 1;
    while(dopingRuntime(current, current < end, &info)){
        // Statement without dynamic optimization
        for(; current < end; current++){
            printf("Print statement without dynamic compilation :(\n");
        }
    }

    printf("\nExample 2: Single statement with a compile-time parameter\n");
    dopinginfo info2 = {
        .iteration_start = 0,
        .iteration_space = 1,
        .source = "\n"
            "#include <stdio.h>\n"
            "int function(){\n"
            "   int N = /*<DOPING N >*/;"
            "   for(int i=0; i < 1; i++) {\n"
            "       printf(\"Compile-time parameter N = %d \\n\", N);\n"
            "   }\n"
            "   return 0;\n"
            "}\n",
        .parameters="N:10",
        .compiler_command="gcc ",
    };

    int current2 = 0;
    int end2 = 1;
    while(dopingRuntime(current2, current2 < end2, &info2)){
        // Statement without dynamic optimization
        for(; current2 < end2; current2++){
            printf("Print statement without dynamic compilation :(\n");
        }
    }

    printf("\nExample 3: Single statement with a compile-time parameter\n");
    printf("and in/out values\n");
    dopinginfo info3 = {
        .iteration_start = 0,
        .iteration_space = 1,
        .source = "\n"
            "#include <stdio.h>\n"
            "#include <stdarg.h>\n"
            "int function(int a, va_list args){\n"
            "   int * written_scalar = va_arg(args, int*);\n"
            "   int * pointer_to_value = va_arg(args, int*);\n"
            "   int N = /*<DOPING N >*/;"
            "   for(int i=0; i < 1; i++) {\n"
            "       printf(\"Compile-time execution\\n\");\n"
            "       *written_scalar = N * *pointer_to_value;\n"
            "   }\n"
            "   printf(\"Compile-time value = %d \\n\", *written_scalar);\n"
            "   return 0;\n"
            "}\n",
        .parameters="N:2",
        .compiler_command="gcc ",
    };

    int current3 = 0;
    int end3 = 1;
    int written_scalar = 5;
    int value = 10;
    int * pointer_to_value = &value;
    while(dopingRuntime(current3, current3 < end3, &info3, &written_scalar, pointer_to_value)){
        // Statement without dynamic optimization
        for(; current3 < end3; current3++){
            printf("Print statement without dynamic compilation :(\n");
            written_scalar = *pointer_to_value;
        }
    }

    printf("This example should make %d == 20\n", written_scalar);

    printf("\nExample 4: Single statement with a conditional compile-time parameter\n");
    printf("and in/out values\n");
    dopinginfo info4 = {
        .iteration_start = 0,
        .iteration_space = 1,
        .source = "\n"
            "#include <stdio.h>\n"
            "#include <stdarg.h>\n"
            "int function(int a, va_list args){\n"
            "   int * /*<DOPING_IF RESTRICT __restrict >*/ written_scalar = va_arg(args, int*);\n"
            "   int * /*<DOPING_IF RESTRICT __restrict >*/ pointer_to_value = va_arg(args, int*);\n"
            "   int N = /*<DOPING N >*/;"
            "   for(int i=0; i < 1; i++) {\n"
            "       printf(\"Compile-time execution\\n\");\n"
            "       *written_scalar = N * *pointer_to_value;\n"
            "   }\n"
            "   printf(\"Compile-time value = %d \\n\", *written_scalar);\n"
            "   return 0;\n"
            "}\n",
        .parameters="N:2,RESTRICT:1",
        .compiler_command="gcc ",
    };

    int current4 = 0;
    int end4 = 1;
    written_scalar = 0;
    while(dopingRuntime(current4, current4 < end4, &info4, &written_scalar, pointer_to_value)){
        // Statement without dynamic optimization
        for(; current4 < end4; current4++){
            printf("Print statement without dynamic compilation :(\n");
            written_scalar = *pointer_to_value;
        }
    }

    printf("This example should make %d == 20\n", written_scalar);

    return 0;
}
