#ifndef DYNAMICFUNCTION_H
#define DYNAMICFUNCTION_H

#include <string>


// Function pointer prototpye:
//   - Input argument is a struct with references to all access values.
//   - Return value is a bool specifying if the loop should still continue.
typedef int (*function_prototype)(int, va_list);

class DynamicFunction {

    function_prototype functionPointer;
    std::string rendered_source;
    void * linked_library;

    public:
        DynamicFunction(
                const std::string& source,
                const std::string& parameters);
        ~DynamicFunction();
        void compile_and_link(const std::string& compilercmd);
        std::string get_rendered_source(){return this->rendered_source;}
        function_prototype get_fp(){return this->functionPointer;}
        int run(int current_iteration, va_list arguments);
};

#endif
