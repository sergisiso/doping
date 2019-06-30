#include "DynamicFunction.h"
#include "SourceRenderingEngine.h"
#include "log.h"

#include <fstream>
#include <cerrno>
#include <cstring>
#include <map>
#include <sstream>
#include <dlfcn.h>
#include <stdio.h>


using namespace std;

struct DynamicOptimizationException : public exception {
    const char * what () const throw () {
        return "Dynamic Optimization Exception";
    }
};

string run_shell(const string& cmd) {
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

DynamicFunction::DynamicFunction(const string& source,
                                 const string& parameters,
                                 const string& compilercmd){

    LOG(INFO) << "Creating DynamicFunction";

    // Could use /tmp but it may be system-specific and
    // could be a security issue (it is a shared folder).
    string filename = "./doping_tmp_file.c";

    // Open a temporal file (is it possible to compile from a stream instead?)
    ofstream tmpfile(filename, ofstream::out | ofstream::trunc);
    if( tmpfile.fail() || !tmpfile.is_open()){
        LOG(ERROR) << " Error opening" << filename << "file: (errno" \
            << errno <<") " << strerror(errno);
        throw DynamicOptimizationException();
    }

    // Transform comma-separated list into parameters map
    map<string, string> parmap;
    stringstream ss1(parameters);
    while(ss1.good()){
        string stringpair;
        getline(ss1, stringpair, ',');
        size_t pos = stringpair.find(':');

        if (pos!=std::string::npos){
            string key = stringpair.substr(0,pos);
            string value = stringpair.substr(pos + 1);
            parmap[key] = value;
        } /*else{
            LOG(ERROR) << " Failed to parse parameters.";
            throw DynamicOptimizationException();
        }*/
    }

    // Render the source with the given parameters
    string newsource = render(source, parmap);
    this->testbuffer.append(newsource);
    LOG(INFO) << " Rendered source = " << newsource;

    // NOTE: An option here would be to encapsulate rendered source
    // in a function that passes parameters and functions used?
    // Delegate the responsability to the passed source for now.

    // Write the output into the temporal file 
    tmpfile << newsource;
    tmpfile.close();
    LOG(INFO) << " Rendered new source into: " << filename;

    // Compile with -fPIC and -shared flags in addition to the original ones
    string libname = "./doping_tmp_object.so";
    string command = compilercmd + " -fPIC -shared " + filename + " -o " + libname;
    LOG(DEBUG) << "Compiling: " << command;
	string result = run_shell(command);
    LOG(DEBUG) << result;
    if ( remove(filename.c_str())!= 0 ){
        LOG(ERROR) << "Could not delete the file:" << filename;
    }



    // Link new object file to current executable
    void * lib = dlopen(libname.c_str(), RTLD_NOW);
    if (!lib) {
        LOG(ERROR) << " Failed to open library .so: \n" << dlerror();
        throw DynamicOptimizationException();
    }
	LOG(DEBUG) << libname << " linked!";
    this->functionPointer = (function_prototype) dlsym(lib, "function");
    if(!this->functionPointer){
        LOG(ERROR) << " Failed to locate function: \n" << dlerror();
        throw DynamicOptimizationException();
    }
	LOG(DEBUG) << " Loop symbol resolved";

    if ( remove(libname.c_str())!= 0 ){
        LOG(ERROR) << "Could not delete the file:" << libname;
    }
    // Note that I am not calling dlclose() anywhere. Fix?
    // I can delete test.c and test.so here?
}






DynamicFunction::~DynamicFunction(){
    LOG(INFO) << "Dynamic Function destructed";

}

int DynamicFunction::run(){
    return this->functionPointer();
}


#ifdef UNIT_TEST
#include "catch.hpp"
TEST_CASE("Test DynamicFunction") {

    SECTION("Simple code"){
        string source = "\n"
            "int sum(){\n"
            "    int sum; /* Unrelated comment */\n"
            "    for(int i; i < /*<DOPING N >*/; i++){\n"
            "        sum += i;\n"
            "    }\n"
            "}\n";
        string parameters = "N:1,A:3";
        string cmd = "gcc ";
        //DynamicFunction df(source, parameters, cmd);
        //REQUIRE(df.getTestBuffer() == "aa");
        REQUIRE("bb" == "aa");
    }
}
#endif



