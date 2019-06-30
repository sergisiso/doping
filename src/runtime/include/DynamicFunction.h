#ifndef DYNAMICFUNCTION_H
#define DYNAMICFUNCTION_H

#include <string>

typedef void (*function_prototype)(va_list);

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
        int somefunc();
        std::string getTestBuffer(){return testbuffer;}
};

#endif
