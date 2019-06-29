#include "dopingRuntime.h"

#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>

#include <cstdarg>
#include <cerrno>
#include <cstring>

#include <unistd.h>
#include <stdlib.h>
#include <time.h>
#include <dlfcn.h>

#include "utils/log.h"


using namespace std;

string specialize_function(const string& fname, int num_parameters, ...);
bool link_specialized_fn(const string& libname);
typedef void (*pf)(va_list);
pf function;

/*
Converts file name to a specialized filename using runtime values one e.g.:
/path/file.cc to /path/file.10.33.cc
*/
string get_specialized_filename(const string& fname, int num_parameters, va_list args){
    string newfname = fname.substr(0,fname.find_last_of("."));
    string extension = fname.substr(fname.find_last_of("."));

    // For each parameter conncatenate value on the filename
    for(int i = 0; i < num_parameters; i++){
        string new_name(va_arg(args, char *));
        string new_value(va_arg(args, char *));
        newfname = newfname + "." + new_value;
    }
    
    return newfname + extension;
}

string specialize_function(const string& fname, int num_parameters, va_list args){

    // Open input file and get all the contents
    ofstream insource (fname.c_str(), ios::in);
    if( insource.fail() || !insource.is_open()){
        LOG(ERROR) << "Error opening" << fname << "file: (errno" \
            << errno << ") " << strerror(errno);
        exit(1);
    }

    //Read the content
    stringstream ss;
    ss << insource.rdbuf();
    string content = ss.str();
    insource.close();

    // Generate specialized file name
    LOG(DEBUG) << "Specializing function" << fname << " with " \
        << num_parameters <<" parameters:";

    // TODO: I repeat part of get_specialized_filename, can it be simplified?
    //string newfname = get_specialized_filename(fname, num_parameters, args);
    string newfname = fname.substr(0,fname.find_last_of("."));
    string extension = fname.substr(fname.find_last_of("."));

    // For each parameter conncatenate value on the filename
    for(int i = 0; i < num_parameters; i++){
        LOG(DEBUG) << "Parameter" << i;
        string new_name(va_arg(args, char *));
        string new_value(va_arg(args, char *));
        newfname = newfname + "." + new_value;
        LOG(DEBUG) << " - " << new_name << " as " << new_value;

        // Replace placeholders on the file contents for the runtime-constant
        const string placeholder = "dopingPLACEHOLDER_" + new_name;
        size_t index;
        /*new_value.find(placeholder);
        if (index != std::string::npos){
            LOG(ERROR) << "String " << new_value << " includes " \
                << placeholder << ", this will generate and infinite substitution sequence.";
            exit(-1);
        }*/
        while(true){
            index = content.find(placeholder);
            if (index == std::string::npos) break;
            content.replace(index, placeholder.length(), new_value);
        }


    }
    
    newfname = newfname + extension;
    LOG(DEBUG) << "New function filename: " << newfname;
    LOG(DEBUG) << "Content: \n" << content;

    // Write specialized source into the file
    ofstream outsource (newfname.c_str(), ios::out | ios::trunc);
    if( outsource.fail() || !outsource.is_open()){
        LOG(ERROR) << " Error opening" << newfname << "file: (errno" \
            << errno <<") " << strerror(errno);
        exit(1);
    }
    outsource << content;
    outsource.close();

    return newfname;
}

string exec(const string& cmd) {
    char buffer[128];
    std::string result = "";
    FILE* pipe = popen( (cmd + " 2>&1").c_str(), "r");
    if (!pipe){
		LOG(ERROR) << "popen() failed";
		exit(-1);
	}

    while (!feof(pipe)) {
    	if (fgets(buffer, 128, pipe) != NULL) result += buffer;
    }
    pclose(pipe);
    return result;
}

string compile_spezialized_fn(const string& specfname, const string& flags){
    
    // Compile with -fPIC and -shared flags in addition to the original ones
    string libname = specfname + ".so";
    string command = flags + " -fPIC -shared " + specfname + " -o " + libname;
    LOG(DEBUG) << "Compiling: " << command;
	string result = exec(command);
    LOG(DEBUG) << result;
  	return libname;
}

bool link_specialized_fn(const string& libname){

    // Link new object file to current executable
    void * lib = dlopen(libname.c_str(), RTLD_NOW);
    if (!lib) {
        LOG(ERROR) << "Failed to open library .so: \n" << dlerror();
        exit(3);
    }
	LOG(DEBUG) << libname << " linked!";
    function = (pf) dlsym(lib,"loop");
    if(!function){
        LOG(ERROR) << "Failed to locate function: \n" << dlerror();
        exit(2);
    }
	LOG(DEBUG) << "Loop symbol resolved";
    //Note that I am not calling dlclose() anywhere. Fix?
}

time_t doping_set_timer(){
    return time(NULL) + 2;
}

int dopingRuntime(int current_iteration, int continue_condition, dopinginfo * loop){

    // If iteration space has finished, do nothing and return
    if (!continue_condition) return continue_condition;
    
    LOG(INFO) << "Entering Doping Runtime with parameters: ";
    LOG(INFO) << " current_iteration=" << current_iteration;
    //LOG(INFO) << " name=" << loop->name;
    LOG(INFO) << " flags=" << loop->flags;
    //LOG(INFO) << " timer=" << loop->timer;
    LOG(INFO) << " iteration_start=" << loop->iteration_start;
    LOG(INFO) << " iteration_space=" << loop->iteration_space;
    LOG(INFO) << " source=" << loop->source;
    LOG(INFO) << " stage=" << loop->stage;
    LOG(INFO) << " parameters=" << loop->parameters;
        
    float progress = float(current_iteration) / \
                     (loop->iteration_space - loop->iteration_start);
    float threshold = 0.5;

    if ( (progress < threshold) ){
        chrono::time_point<chrono::system_clock> tstart, tend;
        tstart = chrono::system_clock::now();
     
        //LOG(INFO) << "Runtime Analysis of: " << loop->name ;
        LOG(INFO) << "Loop at iteration: " << current_iteration << " (" << 100*progress \
            << " %) (Est. Remaining time: " << 2/progress << " s)";
        LOG(INFO) << progress << " < " << threshold << " -> Decided to recompile";
    }

    //loop->timer = doping_set_timer();
    return continue_condition;
}

int dopingRuntime_old( const char * fname, const char * flags, time_t * dopingEnd, int * iter, \
        int start_iter, int iterspace, int continue_loop, \
        unsigned num_runtime_ct, ...){

    // Get working dir
    char cwd[1024];  getcwd(cwd, sizeof(cwd));

    // Compute progress through loop iteration space
    float progress = float(*iter)/(iterspace - start_iter);
    float threshold = 0.5;
   
    //Check if the optimized function is already compiled and linked
    if(false) {
    //if(function != NULL) { // need to make this loop dependant
        LOG(INFO) << "Specialized loop already linked. Executing ...";
        va_list args;
        va_start(args, num_runtime_ct);
        get_specialized_filename(fname, num_runtime_ct, args); // consumes some va args
        function(args);
        va_end(args);
        return false;
    //}
    // Check if optimized library is already compiled from a previous executions
    // else if( access( libname, F_OK ) != -1) { 
    //    LOG(INFO, "Specialized loop %s already compiled. Linking and executing  ...", libname);
    //     link_specialized_fn(libname);
    //     function(args);
    //     return false;
    }else{

        if ( ( *iter > start_iter ) && ( progress < threshold) ){
            chrono::time_point<chrono::system_clock> tstart, tend;

            tstart = chrono::system_clock::now();
            // Recompile loop and continue execution
            LOG(INFO) << "Runtime Analysis of: " << fname ;
            LOG(INFO) << "Loop at iteration: " << *iter << " (" << 100*progress \
                << " %) (Est. Remaining time: " << 2/progress << " s)";
            LOG(INFO) << progress << " < " << threshold << " -> Decided to recompile";

            va_list args;
            va_start(args, num_runtime_ct);
            string specfname = specialize_function(fname, num_runtime_ct, args);

            string libname = compile_spezialized_fn(specfname, flags);
            link_specialized_fn(libname);

            tend = chrono::system_clock::now();
            chrono::duration<double> elapsed_seconds = tend-tstart;
            LOG(INFO) << "doping Runtime elapsed time (inc. recompile and relink): " \
                << elapsed_seconds.count() << " s"; 

            LOG(DEBUG) << "Running optimized function...";
            function(args);

            // Free memory
            va_end(args);
            return false;
        }else{
            // Continue original loop setting a new stop timer
            *dopingEnd = time(NULL) + 2;
            return continue_loop;
        }
    }

}

