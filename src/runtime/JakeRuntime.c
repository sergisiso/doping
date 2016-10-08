#include "JakeRuntime.h"


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

char* specialize_function(char const * fname, int num_parameters, ...){
    va_list list;
    printf("Specializing %s\n", fname);
    // Generate specialized file name
    size_t str_len = strlen(fname) + 1;
    char * newfname = (char *)malloc(str_len);
    strncpy(newfname, fname, strrchr(fname,'.') - fname);

    va_start(list, num_parameters);
    for(int i = 0; i < num_parameters; i++){
        char const * new_name = va_arg(list, char const *);
        char const * new_value = va_arg(list, char const *);
        str_len += strlen(new_value) + 1; // +1 for the underscore
        newfname = (char *) realloc(newfname,str_len);
        strncat(strncat(newfname,"_",str_len),new_value,str_len);
    }
    va_end(list);
    strncat(newfname,strrchr(fname,'.'),str_len);
    
    printf("%s \n", newfname);
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
    va_start(list, num_parameters);
    for(int i = 0; i < num_parameters; i++){
        char const * new_name = va_arg(list, char const *);
        char const * new_value = va_arg(list, char const *);
        char const * tag = "JAKEPLACEHOLDER_";
        char * placeholder = (char *) malloc(strlen(tag)+strlen(new_name));
        strcpy(placeholder,tag);
        strcat(placeholder,new_name);
        str_replace(fcontent,placeholder,new_value);
    }
    va_end(list);
    
    // Write specialized file
    FILE * fo = (FILE*) fopen(newfname,"w");
    fprintf(fo, "%s", fcontent);
    fclose(fo);

    return newfname;
}

/*
int main(){
    printf("testing variadic function\n");

    specialize_function("/home/sergi/jake/test/matrixmult/mm.jake.loop.cc",1,"MATRIXSIZE","1024");

    return 1;
}*/


bool JakeRuntime(time_t * JakeEnd, unsigned * iter, bool continue_loop){

    *JakeEnd = time(NULL) + 2;
    return continue_loop;
    /*   FROM PYTHON FILE
    

            #file.insert("JAKEend = time(NULL) + 2;")
            #file.insert("JAKElast = time(NULL);")
            #file.insert("struct timespec JAKEend, JAKElast;")
            #file.insert("clock_gettime(CLOCK_MONOTONIC, &JAKEend);")
            #file.insert("clock_gettime(CLOCK_MONOTONIC, &JAKEend);")
            #file.insert("clock_gettime(CLOCK_MONOTONIC, &JAKElast);")


 # Runtime analysis
            #file.insert("float JAKEprogress = float(" + node.cond_variable())
            #file.insertpl(")/(" + node.cond_end_value()  +" - ")
            #file.insertpl(node.cond_starting_value() + ");")
            #file.insert("std::cout << \"Loop at interation \" << x << \" (\" ")
            #file.insertpl("<< JAKEprogress * 100 << \"%)\" << std::endl ;")
            #file.insert("std::cout << \"Estimation of Loop total time: \" <<")
            #file.insertpl(" 2/JAKEprogress << \"secs\" << std::endl ;")


if False:
                file.insert("std::cout << \"I am here\" << std::endl;")        
                # Replace runtime constants
                if len(runtime_constants) > 0:
                    spec_string = "char * specfname = specialize_function("
                    spec_string = spec_string + "\"" +newfname+ "\"" + ", " + str(len(runtime_constants))
                    for v in runtime_constants:
                        file.insert("char JAKEstring"+v.displayname+"[10];")
                        file.insert("sprintf(JAKEstring"+v.displayname+",\"%d\","+v.displayname+");")
                        spec_string = spec_string + ", \"" + v.displayname + "\", JAKEstring"+v.displayname 

                    file.insert(spec_string+");")
                file.insert("std::string command = std::string(\"g++ -fPIC -shared \") + specfname + \" -o \" +specfname+ \".so\";")
                file.insert("std::cout << \"Compiling: \" << command << std::endl;")        
                file.insert("system(command.c_str());")
                #file.insert("system(\"g++ -fPIC -shared \"+specfname+\" -o \"+specfname+\".so\");")

                file.insert("std::cout << \"I am here3\" << std::endl;")        
                def_func_ptr = "typedef void (*pf)("
                for v in arrays:
                    def_func_ptr = def_func_ptr + v.type.spelling + ","
                def_func_ptr = def_func_ptr[:-1] + ");"
                file.insert(def_func_ptr)


                file.insert("const char * err;")
                file.insert("void * lib = dlopen((specfname+std::string(\".so\")).c_str(), RTLD_NOW);")
                file.insert("if (!lib){")
                file.increase_indexation()
                file.insert("printf(\"failed to open library .so: %s \\n\", dlerror());")
                file.insert("exit(1);")
                file.decrease_indexation()
                file.insert("}dlerror();")
                file.insert("pf function = (pf) dlsym(lib, \"loop\");")
                file.insert("err = dlerror();")
                file.insert("if (err){")
                file.increase_indexation()
                file.insert("printf(\"failed to locate function: %s \\n\", err);")
                file.insert("exit(1);")
                file.decrease_indexation()
                file.insert("}")
                callstring = "function("
                for v in arrays:
                    callstring = callstring + v.displayname + ","
                callstring = callstring[:-1] + ");"
                file.insert(callstring)
                file.insert("dlclose(lib);") 



    */


}

