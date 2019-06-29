#include <stdio.h>
#include <dopingRuntime.h>

int main(){

    printf("Starting basic.c\n");

    dopinginfo info = {
        .iteration_start = 0,
        .iteration_space = 1,
        .source = "\n"
            "for() {\n"
            "   printf(\"Print dynamic compiled statement\\n\");\n"
            "}\n",
        .parameters="",
        .flags="",
        .stage=""
    };

    int current = 0;
    int end = 1;
    while(dopingRuntime(current, current < end, &info)){
        // Statement without dynamic optimization
        for(; current < end; current++){
            printf("Print statement without dynamic compilation\n");
        }
    }

    printf("End of basic.c\n");
    return 0;
}
