#ifndef LBE_h
#define LBE_h

#include <iostream>
#include <stdlib.h>
#include <sys/time.h>
#include "../IO/IOReadDevice.hpp"
#include "../common.hpp"
#include "Boundaries.hpp"
#include <cmath>
#include <string.h>

class LBSolver{
    REAL *__restrict__ array_ptr;
    int *__restrict__ lbphi_ptr;
    REAL *__restrict__ array_new_ptr;
    REAL *__restrict__ array_pot_ptr;
    double t_potentials, t_collision_propagation, t_boundaries;

    //Parameters
    REAL postequil;
    REAL *__restrict__ lbbdforcex;
    REAL *__restrict__ lbbdforcey;
    REAL *__restrict__ lbbdforcez;
    REAL *__restrict__ lbtf;
    REAL *__restrict__ lbincp;
    REAL *__restrict__ lbg;

public:
    //Constructors
    LBSolver(IOReadDevice*);
    //Destructors
    ~LBSolver();

    void solve_x_iterations(int iterations);


    // Get methods
    REAL * get_state(){return array_ptr;};
    REAL get_MassSite(int fluid, int x, int y, int z);
    REAL get_FracSite(int fpos, int x, int y, int z);
    REAL get_DirectionSpeedSite(int direction, int x, int y, int z);
    void get_momentum(REAL * momentum);

    //Get aggregated calculation times
    double get_t_potentials(){return t_potentials;};
    double get_t_collision_propagation(){return t_collision_propagation;};
    double get_t_boundaries(){return t_boundaries;};
};
#endif
