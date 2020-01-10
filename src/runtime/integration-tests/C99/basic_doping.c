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

    return 0;
}
