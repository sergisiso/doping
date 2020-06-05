#ifndef LOG_H
#define LOG_H

#include <iostream>

using namespace std;

enum typelog {
    DEBUG_LONG =3,
    DEBUG = 2,
    INFO = 1,
    ERROR = -1
};


class LOG {
public:
    LOG(typelog type) {
        opened = false;
        msglevel = type;
        const char * var = std::getenv("DOPING_VERBOSE");
        try{
            level = std::stoi(var);
        } catch (std::exception const &e){
            level = 0; // By default just print ERRORS
        }
        if(msglevel <= level) {
            opened = true;
            fflush(NULL);
            operator << ("["+getLabel(type)+"] ");
        }
    }
    ~LOG() {
        if(opened) {
            cerr << endl;
        }
    }
    template<class T>
    LOG &operator<<(const T &msg) {
        if(msglevel <= level) {
            cerr << msg;
        }
        return *this;
    }
private:
    bool opened;
    typelog msglevel;
    int level;
    inline string getLabel(typelog type) {
        string label;
        switch(type) {
            case DEBUG_LONG: label = "DEBUG"; break;
            case DEBUG: label = "DEBUG"; break;
            case INFO:  label = "INFO "; break;
            case ERROR: label = "ERROR"; break;
        }
        return label;
    }
};

#endif  /* LOG_H */
