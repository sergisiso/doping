#ifndef DYNAMICFUNCTION_H
#define DYNAMICFUNCTION_H

#include <string>


class DynamicFunction {

    void * function;

    public:
        DynamicFunction(const std::string& source, const std::string& parameters);
        ~DynamicFunction();
        int somefunc();
};

#endif
