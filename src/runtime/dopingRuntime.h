#include <time.h>

#ifdef __cplusplus
#define EXTERNC extern "C"
#else
#define EXTERNC
#endif

typedef struct dopinginfo{
    int starting_iteration;
    int iteration_space;
    int continue_loop;
    time_t timer;
    const char * source;
    const char * name;
    const char * flags;
    const char * parameter_map;
    const char * stage;
}dopinginfo;

time_t doping_set_timer();

EXTERNC int dopingRuntime2(dopinginfo*, int, int);

EXTERNC int dopingRuntime(
        const char * fname,
        const char * flags,
        time_t * dopingEnd,
        int * iter,
        int start_iter,
        int iterspace,
        int continue_loop,
        unsigned num_runtime_ct,
        ...);

