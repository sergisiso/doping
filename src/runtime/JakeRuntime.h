#include <time.h>

#ifdef __cplusplus
#define EXTERNC extern "C"
#else
#define EXTERNC
#endif

EXTERNC bool JakeRuntime(
        const char * fname,
        const char * flags,
        time_t * JakeEnd,
        unsigned * iter,
        unsigned start_iter,
        unsigned iterspace,
        bool continue_loop,
        unsigned num_runtime_ct,
        ...);

