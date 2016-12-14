#include "JakeRuntime.h"

#define ERROR   1
#define WARNING 2
#define MSG     3
#define DEBUG   4

void print(int priority, const char * message, ...){
    va_list args;
    va_start(args, message);
    switch(priority){
        case ERROR:
            printf("JAKE ERROR: ");
            break;
        case WARNING:
            printf("JAKE WARNING: ");
            break;
        case MSG:
            printf("JAKE MSG: ");
            break;
        case DEBUG:
            printf("JAKE DEBUG: ");
            break;
    }
    vprintf(message, args);
    printf("\n");
    va_end(args);

}

int str_replace ( char * string, const char *substr, const char *replacement ){
  char *tok = NULL;
  char *newstr = NULL;
  char *oldstr = NULL;
  /* if either substr or replacement is NULL, duplicate string a let caller handle it */
  if ( substr == NULL || replacement == NULL ) return -1;
  newstr = strdup (string);
  while ( (tok = strstr ( newstr, substr ))){
    oldstr = newstr;
    newstr = (char* ) malloc ( strlen ( oldstr ) - strlen ( substr ) + strlen ( replacement ) + 1 );
    /*failed to alloc mem, free old string and return NULL */
    if ( newstr == NULL ){
      free (oldstr);
      return -2;
    }
    memcpy ( newstr, oldstr, tok - oldstr );
    memcpy ( newstr + (tok - oldstr), replacement, strlen ( replacement ) );
    memcpy ( newstr + (tok - oldstr) + strlen( replacement ), tok + strlen ( substr ), strlen ( oldstr ) - strlen ( substr ) - ( tok - oldstr ) );
    memset ( newstr + strlen ( oldstr ) - strlen ( substr ) + strlen ( replacement ) , 0, 1 );
    free (oldstr);
  }
  string = (char*) realloc(string, strlen(newstr));
  strcpy(string,newstr); 
  return 0;
}

char * specialize_function(char const * fname, int num_parameters, va_list args){
    print(DEBUG, "Specializing function %s with %d parameters:", fname, num_parameters);
    // Generate specialized file name
    size_t str_len = strlen(fname) + 1;
    char * newfname = (char *)malloc(str_len);
    sprintf(newfname, "%s%s", fname, ".");

    for(int i = 0; i < num_parameters; i++){
        char * new_name = va_arg(args, char *);
        char * new_value = va_arg(args, char *);
        print(DEBUG, " - %s as %s", new_name, new_value);
        str_len += strlen(new_value) + 1; // +1 for the underscore
        newfname = (char *) realloc(newfname,str_len);
        sprintf(newfname + strlen(newfname), "%s", new_value);
    }
    
    print(DEBUG, " Specialized function filename: %s \n", newfname);
    exit(0);
    // Substitue JAKE PLACEHOLDERS with appropiate values


    // Open input file and get all the contents    
    FILE * f = (FILE*) fopen(fname,"r");
    fseek(f,0,SEEK_END);
    long size = ftell(f);
    fseek(f,0,SEEK_SET);
    char * fcontent = (char *) malloc(sizeof(char)*size);
    fread(fcontent,1,size,f);
    fclose(f);

    // Replace placeholders for each runtime-constant variable
    for(int i = 0; i < num_parameters; i++){
        char const * new_name = va_arg(args, char const *);
        char const * new_value = va_arg(args, char const *);
        char const * tag = "JAKEPLACEHOLDER_";
        char * placeholder = (char *) malloc(strlen(tag)+strlen(new_name));
        strcpy(placeholder,tag);
        strcat(placeholder,new_name);
        str_replace(fcontent,placeholder,new_value);
    }
    
    // Write specialized file
    FILE * fo = (FILE*) fopen(newfname,"w");
    fprintf(fo, "%s", fcontent);
    fclose(fo);

    return newfname;
}


bool JakeRuntime( const char * fname, time_t * JakeEnd, unsigned * iter, unsigned start_iter, \
        unsigned iterspace, bool continue_loop, unsigned num_runtime_ct, ...){

    // Decide if it is worth to continue with the original loop or 
    // recompile a new version
    float progress = float(*iter)/(iterspace - start_iter);
    float threshold = 0.5;

    if ( ( *iter > start_iter ) && ( progress < threshold) ){
        // Recompile loop and continue execution
        print(MSG,"JAKE Runtime Analysis for %s", fname );
        print(MSG,"Loop at iteration: %u (%f \%) (Remaining time: %f s)", *iter, 100 * progress, 2/progress );
        print(MSG,"%f < %f -> Decided to recompile", progress, threshold );

        // Specialize template function with delayed evaluation parameters
        va_list args;
        va_start(args, num_runtime_ct);
        char * specfname = specialize_function(fname, num_runtime_ct, args);
        va_end(args);
        exit(0);


        // Prepare recompilation command and execute
        char command[1024]; // Implement better solution (with realloc?)
        char libname[1024];

        snprintf(libname, sizeof(libname), "%s%s", specfname, ".so");
        snprintf(command, sizeof(command), "%s%s%s%s", "g++ -fPIC -shared", fname, \
                " -o ", libname);
        printf("Compiling: %s ", command );
        system(command);
        printf("Compilation complete! " );

        // Link new object file to current executable        
        typedef void (*pf)();
        const char* err;

        void * lib = dlopen(libname, RTLD_NOW);
        if (!lib) {
            printf("failed to open library .so: %s \n", dlerror());
            exit(1);
        }dlerror();

        pf function = (pf) dlsym(lib,"function_name");
        if(err){
            printf("failed to open locate function: %s \n", dlerror());
            exit(2);
        }

        function();

        dlclose(lib);

        return false;
    }else{
        // Continue original loop setting a new stop timer
        *JakeEnd = time(NULL) + 2;
        return continue_loop;
    }

}

