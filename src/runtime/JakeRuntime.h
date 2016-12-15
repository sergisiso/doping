#include <stdarg.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <time.h>
#include <dlfcn.h>


typedef struct{
    char * LoopID;
    char * fname;
    char * loop;
    unsigned start_iter;
    unsigned end_iter;
}JAKELoop;

char* specialize_function(char const * fname, int num_parameters, ...);
int str_replace (char * string, const char *substr, const char *replacement );
//bool JakeRuntime(time_t * JakeEnd, unsigned * iter, bool continue_loop);
void JakeLoopInit( );
bool JakeRuntime( const char * fname, time_t * JakeEnd, unsigned * iter, \
        unsigned start_iter, unsigned iterspace, bool continue_loop, \
        unsigned num_runtime_ct, ...);

