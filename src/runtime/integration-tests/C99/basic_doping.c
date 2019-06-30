#include <stdio.h>
#include <dopingRuntime.h>

int main(){

    // Runtime examples with C99 code.

    // Example 1: Single statement without rendering parameters nor data accesses. 
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

    // Example 2

    return 0;
}
