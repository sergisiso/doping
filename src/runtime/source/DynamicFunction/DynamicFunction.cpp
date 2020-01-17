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

static int sNextId = 0;
string getNextId() { return to_string(++sNextId); }

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
                                 const string& parameters){

    LOG(INFO) << "Creating DynamicFunction" << source << parameters;

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
        }
    }

    // Render the source with the given parameters
    string newsource = render(source, parmap);
    LOG(INFO) << " Rendered source = " << newsource;
    this->rendered_source.append(newsource);
}

void DynamicFunction::compile_and_link(const string& compilercmd) {
    // Get a unique ID
    string uid = getNextId();

    // Use /tmp but it may be system-specific and
    // could be a security issue (it is a shared folder).
    string filename = "/tmp/doping_tmp_file_" + uid + ".c";

    // Open a temporal file (is it possible to compile from a stream instead?)
    ofstream tmpfile(filename, ofstream::out | ofstream::trunc);
    if(tmpfile.fail() || !tmpfile.is_open()){
        LOG(ERROR) << " Error opening" << filename << "file: (errno" \
            << errno <<") " << strerror(errno);
        throw std::runtime_error("Error opening " + filename);
    }

    // NOTE: An option here would be to encapsulate rendered source
    // in a function that passes parameters and functions used?
    // Delegate the responsability to the passed source for now.

    // Write the output into the temporal file 
    tmpfile << this->rendered_source;
    tmpfile.close();
    LOG(INFO) << "Rendered new source into: " << filename;
    LOG(INFO) << "Rendered new source into: " << this->rendered_source;

    // Compile with -fPIC and -shared flags in addition to the original ones
    string libname = "/tmp/doping_tmp_object" + uid + ".so";
    string command = compilercmd + " -fPIC -shared " + filename + " -o " + libname;
    LOG(DEBUG) << "Compiling: " << command;
	string result = run_shell(command);
    LOG(DEBUG) << "Compilation output:";
    LOG(DEBUG) << result;
    if ( remove(filename.c_str())!= 0 ){
        throw std::runtime_error("Error deleting " + filename);
        LOG(ERROR) << "Could not delete the file:" << filename;
    }

    // Link new object file to current executable
    void * lib = dlopen(libname.c_str(), RTLD_NOW);
    if (!lib) {
        LOG(ERROR) << "Failed to open library .so: \n" << dlerror();
        throw std::runtime_error("Failed to open library .so");
    }
	LOG(DEBUG) << libname << " linked!";
    this->functionPointer = (function_prototype) dlsym(lib, "function");
    if(!this->functionPointer){
        LOG(ERROR) << "Failed to locate function: \n" << dlerror();
        throw std::runtime_error("Failed to locate function:");
    }
	LOG(DEBUG) << "Loop symbol resolved";

    if ( remove(libname.c_str())!= 0 ){
        LOG(ERROR) << "Could not delete the file:" << libname;
    }
    // Note that I am not calling dlclose() anywhere. Fix?
    // I can delete test.c and test.so here?
}

DynamicFunction::~DynamicFunction(){
    LOG(INFO) << "Dynamic Function destructed";

}

int DynamicFunction::run(int current_iteration, va_list arguments){
    if (this->functionPointer == NULL)
        throw std::runtime_error("Function pointer is not initialized");
    return this->functionPointer(current_iteration, arguments);
}


#ifdef UNIT_TEST
#include "catch.hpp"
SCENARIO("Simple source with no parameters") {

    string source = "\n"
        "int function(){\n"
        "    int sum = 0; /* Unrelated comment */\n"
        "    for(int i = 0; i < 1; i++){\n"
        "        sum += 10;\n"
        "    }\n"
        "    return sum;\n"
        "}\n";

    GIVEN("An empty parameters string"){
        string parameters = "";
        DynamicFunction df(source, parameters);

        WHEN("initialised"){
            THEN ("the rendered code is unmodified"){
                REQUIRE(df.get_rendered_source() == source);
            }
        }
        WHEN("Execute the function before compiling"){
            THEN ("An error is raised"){
                // TODO: REQUIRE_THROWS_AS(df.run(), std::runtime_error);
            }
        }
        WHEN("Exectute the function compiled  with gcc"){
            df.compile_and_link("gcc");
            int retval = df.run(0, NULL);
            THEN ("it links a new function into the functionpointer"){
                REQUIRE(df.get_fp() != NULL);
                REQUIRE(retval == 10);
            }
        }
    }

    GIVEN("An invalid string parameter"){
        string parameters = "invalid";
        DynamicFunction df(source, parameters);
    }
}

SCENARIO("Simple source with 2 parameters") {

    string source = "\n"
        "int function(){\n"
        "    int sum = 0; /* Unrelated comment */\n"
        "    for(int i = 0; i < 1; i++){\n"
        "        sum += /*<DOPING A >*/ + /*<DOPING B >*/;\n"
        "    }\n"
        "    return sum;\n"
        "}\n";

    GIVEN("An empty parameters string"){
        string parameters = "";
        // DynamicFunction df(source, parameters);
        // TODO: Compiler should fail here
    }
    GIVEN("The value of the 2 parameters as 'A:3,B:6'"){
        string parameters = "A:3,B:6";
        DynamicFunction df(source, parameters);

        WHEN("initialised"){
            THEN ("the rendered code is unmodified"){
                string expected = "\n"
                    "int function(){\n"
                    "    int sum = 0; /* Unrelated comment */\n"
                    "    for(int i = 0; i < 1; i++){\n"
                    "        sum += 3 + 6;\n"
                    "    }\n"
                    "    return sum;\n"
                    "}\n";
                REQUIRE(df.get_rendered_source() == expected);
            }
        }
        WHEN("Exectute the function compiled  with gcc"){
            df.compile_and_link("gcc");
            int retval = df.run(0, NULL);
            THEN ("it links a new function into the functionpointer"){
                REQUIRE(df.get_fp() != NULL);
                REQUIRE(retval == 9);
            }
        }
    }
    GIVEN("The value of the 2 parameters as 'A:3,B:6,"){
        string parameters = "A:3,B:6,";
        WHEN("Exectute the function compiled  with gcc"){
            DynamicFunction df(source, parameters);
            df.compile_and_link("gcc");
            int retval = df.run(0, NULL);
            THEN ("it links a new function and returns the correct value"){
                REQUIRE(df.get_fp() != NULL);
                REQUIRE(retval == 9);
            }
        }
    }
    GIVEN("The value of the 2 parameters as '  A:3  ,   B:6 ,  "){
        string parameters = "  A:3  ,   B:6 ,  ";
        // TODO: Make it work or give clean error
        /*WHEN("Exectute the function compiled  with gcc"){
            DynamicFunction df(source, parameters);
            df.compile_and_link("gcc");
            int retval = df.run();
            THEN ("it links a new function and returns the correct value"){
                REQUIRE(df.get_fp() != NULL);
                REQUIRE(retval == 9);
            }
        }*/
    }
}
#endif