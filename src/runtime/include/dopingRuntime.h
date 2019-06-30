#include <time.h>

#ifdef __cplusplus
#define EXTERNC extern "C"
#else
#define EXTERNC
#endif

typedef struct dopinginfo{
    // Starting iteration value (lower end of iteration space).
    int iteration_start;
    // Length of the loop (upper bound - lower bound of iteration space).
    int iteration_space;
    // Source code to be rendered and re-compiled.
    const char * source;
    // Command re-compile the given source code.
    const char * compiler_command;
    // Parameters to render the given source code.
    const char * parameters;
    // Arguments to give to the re-compiled function. This should be all the
    // variables and references used inside the given source.
    int num_arguments;
    void * arguments;
    // Information about the dynamic state?
    // const char * stage;
}dopinginfo;

//time_t doping_set_timer();

// Doping infrastructure entry point.
EXTERNC int dopingRuntime(int, int, dopinginfo*);
