#ifndef LOG_H
#define LOG_H

#include <iostream>

using namespace std;

enum typelog {
    DEBUG,
    INFO,
    WARN,
    ERROR
};


class LOG {
public:
    LOG(typelog type) {
        opened=false;
        msglevel = type;
        verbose = (std::getenv("DOPING_VERBOSE") != NULL);
        operator << ("["+getLabel(type)+"] ");
    }
    ~LOG() {
        if(opened) {
            cerr << endl;
        }
        opened = false;
    }
    template<class T>
    LOG &operator<<(const T &msg) {
        if(msglevel >= DEBUG && verbose) {
            cerr << msg;
            opened = true;
        }
        return *this;
    }
private:
    bool opened;
    bool verbose;
    typelog msglevel;
    inline string getLabel(typelog type) {
        string label;
        switch(type) {
            case DEBUG: label = "DEBUG"; break;
            case INFO:  label = "INFO "; break;
            case WARN:  label = "WARN "; break;
            case ERROR: label = "ERROR"; break;
        }
        return label;
    }
};

#endif  /* LOG_H */
