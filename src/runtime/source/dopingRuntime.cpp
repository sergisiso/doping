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

bool global_counter = 0;

template <typename T, typename U>
int dopingRuntimeG(
        T current_iteration,
        T continue_condition,
        U * loop,
        va_list arguments){
    // If iteration space has finished, do nothing and return
    if (!continue_condition) return continue_condition;

    // If the loop is too small, continue with the original code
    // if (loop->iteration_space < 100) return continue_condition;

    // Forbid nested Doping run-times for now
    if (global_counter > 0) return continue_condition;

    global_counter = 1;

    
    if(loop->name == NULL){
        LOG(INFO) << "Entering unnamed Doping Runtime.";
    }else{
        LOG(INFO) << "Entering Doping Runtime for loop " << loop->name << ".";
    }
    LOG(DEBUG) << " - current_iteration = " << current_iteration;
    LOG(DEBUG) << " - compiler_command = " << loop->compiler_command;
    //LOG(DEBUG) << " - timer=" << loop->timer;
    LOG(DEBUG) << " - iteration_start = " << loop->iteration_start;
    LOG(DEBUG) << " - iteration_space = " << loop->iteration_space;
    LOG(DEBUG_LONG) << " - source: " << loop->source;
    //LOG(DEBUG) << " - stage = " << loop->stage;
    LOG(DEBUG) << " - parameters = " << loop->parameters;
        
    float progress = float(current_iteration) / \
                     (loop->iteration_space - loop->iteration_start);
    //float threshold = 0.5;

    //if ( (progress < threshold) ){
    if ( true ){
        chrono::time_point<chrono::system_clock> tstart, tend;
        tstart = chrono::system_clock::now();
     
        LOG(INFO) << "Runtime Analysis: Loop at " << current_iteration << " (" \
            << 100*progress << " %)"; // (ETC: " << 2/progress << " s)";
        // LOG(INFO) << progress << " < " << threshold << " -> Decided to recompile";
        
        DynamicFunction * df;

        try {
            df = new DynamicFunction(loop->source, loop->parameters);
            df->compile_and_link(loop->compiler_command);
        } catch(exception& e){
            LOG(ERROR) << " Doping failed to dynamically optimize function with error:";
            LOG(ERROR) << e.what();
            LOG(ERROR) << "Continuing with baseline code.";
            global_counter = 0;
            return continue_condition;
        }
        tend = chrono::system_clock::now();
        chrono::duration<double> tduration = tend - tstart;
        LOG(INFO) << "Render template, compilation and linking took: " << tduration.count() \
            << " seconds.";
        if (std::getenv("DOPING_BENCHMARK") != NULL){
            cout << "DopingRuntime: " <<  tduration.count() << " ";
        }

        //unsigned lstart = va_arg(arguments, unsigned);
        //LOG(INFO) << "Argument: " << lstart;
        //T retval =
        tstart = chrono::system_clock::now();
        df->run(current_iteration, arguments);
        tend = chrono::system_clock::now();
        tduration = tend - tstart;

        if (std::getenv("DOPING_BENCHMARK") != NULL){
            cout << "DynFunction: " <<  tduration.count() << " ";
        }

        delete df;
        global_counter = 0;
        return 0; // Assume loop is finished (this may need a more careful solution)
        //return continue_condition; // Run the baseline now (just for testing!!)
    }

    //loop->timer = doping_set_timer();
    return continue_condition;
}
// Check if optimized library is already compiled from a previous executions
// else if( access( libname, F_OK ) != -1) { 
//    LOG(INFO, "Specialized loop %s already compiled. Linking and executing  ...", libname);
//     link_specialized_fn(libname);
//     function(args);
//     return false;
//
//
//


// Specialization of dopingRuntime for the extern "C" (no templates)
int dopingRuntimeU(unsigned current_iteration, unsigned continue_condition,
                  dopinginfoU * loop, ...){
    va_list arguments;
    va_start(arguments, loop);
    return dopingRuntimeG<unsigned, dopinginfoU>(current_iteration, continue_condition,
        loop, arguments);
    va_end(arguments);
}

int dopingRuntime(int current_iteration, int continue_condition,
                  dopinginfo * loop, ...){
    va_list arguments;
    va_start(arguments, loop);
    return dopingRuntimeG<int, dopinginfo>(current_iteration, continue_condition,
        loop, arguments);
    va_end(arguments);
}

