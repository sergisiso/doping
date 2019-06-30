#include "DynamicFunction.h"
#include "catch.hpp"
#include "log.h"

using namespace std;

DynamicFunction::DynamicFunction(const string& source, const string& parameters){

    LOG(INFO) << "Dynamic Function created";

}


DynamicFunction::~DynamicFunction(){
    LOG(INFO) << "Dynamic Function destructed";

}

int DynamicFunction::somefunc(){

}
