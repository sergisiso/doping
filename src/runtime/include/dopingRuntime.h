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
    // Loop Name
    const char * name;
    // Arguments to give to the re-compiled function. This should be all the
    // variables and references used inside the given source.
    int num_arguments;
    void * arguments;
    // Information about the dynamic state?
    // const char * stage;
} dopinginfo;

typedef struct dopinginfoU{
    // Starting iteration value (lower end of iteration space).
    unsigned iteration_start;
    // Length of the loop (upper bound - lower bound of iteration space).
    unsigned iteration_space;
    // Source code to be rendered and re-compiled.
    const char * source;
    // Command re-compile the given source code.
    const char * compiler_command;
    // Parameters to render the given source code.
    const char * parameters;
    // Loop Name
    const char * name;
    // Arguments to give to the re-compiled function. This should be all the
    // variables and references used inside the given source.
    int num_arguments;
    void * arguments;
    // Information about the dynamic state?
    // const char * stage;
} dopinginfoU;

//time_t doping_set_timer();

// Doping infrastructure entry point.
EXTERNC int dopingRuntime(
    int current_iteration,
    int continue_condition,
    dopinginfo * loop,
    ...);

EXTERNC int dopingRuntimeU(
    unsigned current_iteration,
    unsigned continue_condition,
    dopinginfoU * loop,
    ...);
