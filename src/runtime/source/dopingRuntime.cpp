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

template <typename T, typename U>
int dopingRuntimeG(
        T current_iteration,
        T continue_condition,
        U * loop,
        va_list arguments){

    // If iteration space has finished, do nothing and return
    if (!continue_condition) return continue_condition;
    
    LOG(INFO) << "Entering Doping Runtime with parameters: ";
    LOG(INFO) << " - current_iteration = " << current_iteration;
    //LOG(INFO) << " - name=" << loop->name;
    LOG(INFO) << " - compiler_command = " << loop->compiler_command;
    //LOG(INFO) << " - timer=" << loop->timer;
    LOG(INFO) << " - iteration_start = " << loop->iteration_start;
    LOG(INFO) << " - iteration_space = " << loop->iteration_space;
    LOG(INFO) << " - source: " << loop->source;
    //LOG(INFO) << " - stage = " << loop->stage;
    LOG(INFO) << " - parameters = " << loop->parameters;
        
    float progress = float(current_iteration) / \
                     (loop->iteration_space - loop->iteration_start);
    float threshold = 0.5;

    if ( (progress < threshold) ){
        chrono::time_point<chrono::system_clock> tstart, tend;
        tstart = chrono::system_clock::now();
     
        //LOG(INFO) << "Runtime Analysis of: " << loop->name ;
        LOG(INFO) << "Loop at iteration: " << current_iteration << " (" \
            << 100*progress \
            << " %) (Est. Remaining time: " << 2/progress << " s)";
        LOG(INFO) << progress << " < " << threshold << " -> Decided to recompile";
        
        DynamicFunction * df;

        try {
            df = new DynamicFunction(loop->source, loop->parameters);
            df->compile_and_link(loop->compiler_command);
        } catch(exception& e){
            LOG(ERROR) << " Doping failed to dynamically optimize function. "
                "Continuing with baseline code.";
            return continue_condition;
        }
        tend = chrono::system_clock::now();
        chrono::duration<double> tduration = tend - tstart;
        LOG(INFO) << "Compilation and linking took: " << tduration.count() \
            << " seconds.";

        //unsigned lstart = va_arg(arguments, unsigned);
        //LOG(INFO) << "Argument: " << lstart;
        T retval = df->run(current_iteration, arguments);

        delete df;
        return retval;
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
unsigned dopingRuntimeU(unsigned current_iteration, unsigned continue_condition,
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

