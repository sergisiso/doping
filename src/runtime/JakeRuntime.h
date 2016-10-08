#include <stdarg.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

char* specialize_function(char const * fname, int num_parameters, ...);
int str_replace (char * string, const char *substr, const char *replacement );
bool JakeRuntime(time_t * JakeEnd, unsigned * iter, bool continue_loop);
