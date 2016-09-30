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
