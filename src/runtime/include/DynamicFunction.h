#ifndef DYNAMICFUNCTION_H
#define DYNAMICFUNCTION_H

#include <string>


// Function pointer prototpye:
//   - Input argument is a struct with references to all access values.
//   - Return value is a bool specifying if the loop should still continue.
typedef int (*function_prototype)();

class DynamicFunction {

    function_prototype functionPointer;
    //hash<string> functionID;
    std::string testbuffer;

    public:
        DynamicFunction(
                const std::string& source,
                const std::string& parameters,
                const std::string& compilercmd);
        ~DynamicFunction();
        int run();
        std::string getTestBuffer(){return testbuffer;}
};

#endif
