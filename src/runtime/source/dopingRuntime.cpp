#include "dopingRuntime.h"

#include <string>
#include <chrono>

#include <cstdarg>

#include <unistd.h>
#include <stdlib.h>
#include <time.h>

#include "log.h"
#include "DynamicFunction.h"


using namespace std;

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

        DynamicFunction df = DynamicFunction(
                loop->source,
                loop->parameters,
                loop->flags);
        df.somefunc();

    }

    //loop->timer = doping_set_timer();
    return continue_condition;
}

/*
int dopingRuntime_old( const char * fname, const char * flags, time_t * dopingEnd, int * iter, \
        int start_iter, int iterspace, int continue_loop, \
        unsigned num_runtime_ct, ...){

    // Get working dir
    char cwd[1024];  getcwd(cwd, sizeof(cwd));

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
*/
