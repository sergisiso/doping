#include "LBSolver.hpp"
#include <iomanip>
#define COLTILE 1
#define POTTILE 1

using namespace std;


void pprint(REAL *array){
    cout << "----- x-y array view -----" << endl;
    for(int x=0; x<TSIZE; x++){
        for(int y=0; y<TSIZE; y++){
            cout << std::setprecision(3) << array[index(x,y,FIRST,0,0)] << "\t";
        }
        cout << endl;
    }
}


LBSolver::LBSolver(IOReadDevice *read){
    read->fDefineSystem("input/lbin.sys");
    array_ptr =     (REAL *) _mm_malloc(t_total() * sizeof(REAL), 64);
    array_new_ptr = (REAL *) _mm_malloc(t_total() * sizeof(REAL), 64);
    array_pot_ptr = (REAL *) _mm_malloc(t_pot() * sizeof(REAL), 64);
    lbphi_ptr =     (int *)  _mm_malloc(t_phi() * sizeof(int), 64);
    memset(lbphi_ptr,0,t_phi()*sizeof(int));

    read->fInputParameters("input/lbin.sys");
    read->initialize_array(array_ptr);

    postequil = read->Parameters.postequil;
    lbbdforcex = (REAL*) malloc(sizeof(REAL)*FLUIDS);
    lbbdforcey = (REAL*) malloc(sizeof(REAL)*FLUIDS);
    lbbdforcez = (REAL*) malloc(sizeof(REAL)*FLUIDS);

    for(int i=0;i<FLUIDS;i++){
        lbbdforcex[i] = read->Parameters.lbbdforce[i*3];
        lbbdforcey[i] = read->Parameters.lbbdforce[i*3+1];
        lbbdforcez[i] = read->Parameters.lbbdforce[i*3+2];
    }
    

    lbtf = read->Parameters.lbtf;
    lbincp = read->Parameters.lbincp;
    lbg = read->Parameters.lbg;
    //std::copy(read->Parameters.lbtf,read->Parameters.lbtf+FLUIDS, lbtf);
    //std::copy(read->Parameters.lbincp, read->Parameters.lbincp+FLUIDS,lbincp);
    //std::copy(read->Parameters.lbg, read->Parameters.lbg+FLUIDS*FLUIDS, lbg);

   t_potentials = 0.0, t_collision_propagation=0.0, t_boundaries=0.0;
}

LBSolver::~LBSolver(){
    _mm_free(array_ptr);
    _mm_free(array_pot_ptr);
    _mm_free(array_new_ptr);
}


void LBSolver::solve_x_iterations(int iterations){
    
    double t_counter_end, t_counter_start;

    // Requiered for good memory access performance
    REAL* __restrict__ array = array_ptr;
    int* __restrict__ lbphi = lbphi_ptr;
    REAL* __restrict__ array_new = array_new_ptr;
    REAL* __restrict__ array_pot = array_pot_ptr;
    __assume_aligned(array, 64);
    __assume_aligned(array_new, 64);
    __assume_aligned(array_pot, 64);


#ifdef DEBUG
    cout << "Parameters --------------" << endl;
    cout << "Postequil: " << postequil << endl;
    cout << "lbbdforcex: ";
    for(int i=0; i < FLUIDS; i++)cout << std::setprecision(3) << lbbdforcex[i] << " ";
    cout << endl << "lbbdforcey: ";
    for(int i=0; i < FLUIDS; i++)cout << std::setprecision(3) << lbbdforcey[i] << " ";
    cout << endl << "lbbdforcez: ";
    for(int i=0; i < FLUIDS; i++)cout << std::setprecision(3) << lbbdforcez[i] << " ";
    cout << endl << "lbtf: ";
    for(int i=0; i < FLUIDS; i++)cout << std::setprecision(3) << lbtf[i] << " ";
    cout << endl << "lbincp: ";
    for(int i=0; i < FLUIDS; i++)cout << std::setprecision(3) << lbincp[i] << " ";
    cout << endl << "lbg: ";
    for(int i=0; i < FLUIDS*FLUIDS; i++)cout << std::setprecision(3) << lbg[i] << " ";
    cout << endl;   
#endif
    REAL momentum[3] = {0.0,0.0,0.0};

    // Main compute loop
    double t_alloc = dtime();
    for(int iter=0; iter<iterations; iter++){

        copy_2halo_layers(array);

#ifdef DEBUG
        this->get_momentum(momentum);
        cout << "Momentum: "<< momentum[0] << endl;
        pprint(array);
        if(iter == 1) exit(0);
#endif
        t_counter_start = dtime();
        // Calculate Potential of each particle
        #pragma omp parallel for schedule(static) collapse(2)
        for(unsigned xx=0; xx<TSIZE; xx+=POTTILE){
        for(unsigned yy=0; yy<TSIZE; yy+=POTTILE){
        for(unsigned x=xx; x<min(xx+POTTILE,unsigned(TSIZE)); x++){
        for(unsigned y=yy; y<min(yy+POTTILE,unsigned(TSIZE)); y++){
        #pragma omp simd
        for(int z=0; z<TSIZE; z++){
            for(int f=0; f<FLUIDS; f++) {
                REAL mass=0.0;
                for( int l=0; l<LATS; l++){
                    mass += array[index(x,y,z,f,l)];
                }
                array_pot[indexpot(x,y,z,f)] = lbincp[f] * (1.0 - exp(-mass)/lbincp[f]);
            }
        }
        }
        }}}
        t_counter_end = dtime();
        t_potentials += t_counter_end - t_counter_start;

#ifdef DEBUG
        cout << "ArrayPot: ";
        for(int i=0; i < 10; i++)cout << std::setprecision(3) << array_pot[i] << " ";
        cout << endl;
#endif

        t_counter_start = dtime();
        // Compute interaction forces, collition and propagation
        #pragma omp parallel for schedule(static) collapse(2)
        for(unsigned xx=HIniIn; xx<=HEndIn; xx+=COLTILE){
        for(unsigned yy=HIniIn; yy<=HEndIn; yy+=COLTILE){
        for(unsigned x=xx; x<min(xx+COLTILE,unsigned(HEndIn+1)); x++){
        for(unsigned y=yy; y<min(yy+COLTILE,unsigned(HEndIn+1)); y++){
        #pragma omp simd
        for(int z=HIniIn; z<=HEndIn; z++){
            REAL factorx[FLUIDUPPERBOUND] = {0.0};
            REAL factory[FLUIDUPPERBOUND] = {0.0};
            REAL factorz[FLUIDUPPERBOUND] = {0.0};
        

            REAL particle_speedx = 0.0;
            REAL particle_speedy = 0.0;
            REAL particle_speedz = 0.0;
            REAL particle_mass = 0.0;

            //Compute particle mass and speed
            REAL fluid_mass=0.0;
            for(long fluid=0; fluid<FLUIDS; fluid++){
                for(int l=0; l<LATS; l++) {
                    particle_mass += array[index(x,y,z,fluid,l)];
                    particle_speedx += array[index(x,y,z,fluid,l)] * lbvx[l];
                    particle_speedy += array[index(x,y,z,fluid,l)] * lbvy[l];
                    particle_speedz += array[index(x,y,z,fluid,l)] * lbvz[l];
                }
            }
            const REAL particle_inverse_mass = 1.0/particle_mass;
            particle_speedx *= particle_inverse_mass;
            particle_speedy *= particle_inverse_mass;
            particle_speedz *= particle_inverse_mass;
            
            // Compute particle factors
            if(lbphi[indexphi(x,y,z)] == 0){
                for(int lattice=1;lattice<LATS; lattice++){
                    //const int spos = neigh_index(x,y,z,0,lattice);
                    // const double spsi = (lbneigh[index(x,y,z,fluid,lattice)]>0 &&
                    //                     lbphi[spos]>10);
                    //wfactor += lbvw[lattice] * spsi;

                    for(int fluid=0; fluid<FLUIDS; fluid++){
                        const REAL psi = array_pot[indexpot_neighbour(x,y,z,fluid,lattice)];
                        factorx[fluid] += lbvwx[lattice] * psi;
                        factory[fluid] += lbvwy[lattice] * psi;
                        factorz[fluid] += lbvwz[lattice] * psi;
                    }
                }
            }

            //Compute particle temperature
            if(lbphi[indexphi(x,y,z)]<11){
                //Do something
            }

            // Collide and propagate
            for(int fluid=0; fluid<FLUIDS; fluid++){
                REAL fluid_mass=0.0;
                REAL interforce_local_x=0.0;
                REAL interforce_local_y=0.0;
                REAL interforce_local_z=0.0;
                
                for(int lattice=0; lattice<LATS; lattice++) {
                    fluid_mass += array[index(x,y,z,fluid,lattice)];
                }
                

                // Shan Chen interaction
                if(lbphi[indexphi(x,y,z)] == 0.0){
                    const REAL psik = std::abs(array_pot[indexpot(x,y,z,fluid)]);
                    for(int fluid2=0; fluid2<FLUIDS; fluid2++){
                        REAL gfluid = lbg[fluid*FLUIDS+fluid2] * psik;
                        interforce_local_x-=gfluid*factorx[fluid2];
                        interforce_local_y-=gfluid*factory[fluid2];
                        interforce_local_z-=gfluid*factorz[fluid2];
                    }
                }


                // Collision
                if(lbphi[indexphi(x,y,z)] != 11){
                    interforce_local_x += postequil * lbbdforcex[fluid];
                    interforce_local_y += postequil * lbbdforcey[fluid];
                    interforce_local_z += postequil * lbbdforcez[fluid];
                    if(lbphi[indexphi(x,y,z)] != 12 && lbphi[indexphi(x,y,z)] !=13){
                        const REAL invmass = 1.0/fluid_mass;
                        const REAL invmassrelax = invmass/lbtf[fluid];
                        const REAL relax = 1.0 - lbtf[fluid];
                        const REAL sx = particle_speedx + interforce_local_x * invmassrelax;
                        const REAL sy = particle_speedy + interforce_local_y * invmassrelax;
                        const REAL sz = particle_speedz + interforce_local_z * invmassrelax;
                        const REAL speed_mod = sx*sx + sy*sy + sz*sz;

                        for(int l=0; l<LATS; l++){
                            const REAL uv=lbvx[l]*sx+lbvy[l]*sy+lbvz[l]*sz;
                            const REAL feq=fluid_mass*lbw[l]*(1+3.0*uv+4.5*uv*uv-1.5*speed_mod);

                            // Streaming step
                            array_new[index_neighbour(x,y,z,fluid,l)] = relax * array[index(x,y,z,fluid,l)] + feq*lbtf[fluid];
                        }
                    }
                }
            }
        }
        }
        }}}
        t_counter_end = dtime();
        t_collision_propagation += t_counter_end - t_counter_start;

        t_counter_start = dtime();
        // Array swap
        swap(array_new, array);
        // Boundary conditions
        t_counter_end = dtime();
        t_boundaries += t_counter_end - t_counter_start;
    }

    // Give the class pointers the proper final state
    array_ptr = array;
    array_new_ptr = array_new;
}


void LBSolver::get_momentum(REAL * momentum){
    REAL *__restrict__ array = array_ptr;

    REAL momentum_x = 0;
    REAL momentum_y = 0;
    REAL momentum_z = 0;
    #pragma omp parallel for schedule(static) reduction(+:momentum_x,momentum_y,momentum_z) collapse(2)
    for(int x=FIRST; x<=LAST; x++){
    for(int y=FIRST; y<=LAST; y++){
    #pragma omp simd reduction(+:momentum_x,momentum_y,momentum_z)
    for(int z=FIRST; z<=LAST; z++){
        for(int fluid=0; fluid<FLUIDS; fluid++){
            for(int lattice=0; lattice<LATS; lattice++){
                momentum_x += array[index(x,y,z,fluid,lattice)] * lbvx[lattice];
                momentum_y += array[index(x,y,z,fluid,lattice)] * lbvy[lattice];
                momentum_z += array[index(x,y,z,fluid,lattice)] * lbvz[lattice];
            }
        }
    }
    }
    }

    momentum[0] = momentum_x;
    momentum[1] = momentum_y;
    momentum[2] = momentum_z;
}

REAL LBSolver::get_MassSite(int fluid, int x, int y, int z){
    REAL mass = 0.0;
    for(int l=0; l<LATS; l++){
        mass += array_ptr[index(x,y,z,fluid,l)];
    }
    return mass;
}

REAL LBSolver::get_FracSite(int fpos, int x, int y, int z){
    // TODO: Implement,  what does exaclty does?
    return 1.0;
}

REAL LBSolver::get_DirectionSpeedSite(int direction, int x, int y, int z){

    REAL speed = 0;
    REAL mass=0.0;
    for(int f=0; f<FLUIDS; f++) {
        mass += array_ptr[index(x,y,z,f,0)];
        for(int l=0; l<LATS; l++){
            if(direction == 0) speed += array_ptr[index(x,y,z,f,l)] * lbvx[l];
            if(direction == 1) speed += array_ptr[index(x,y,z,f,l)] * lbvy[l];
            if(direction == 2) speed += array_ptr[index(x,y,z,f,l)] * lbvz[l];
        }
    }

    return float(speed*(1.0/mass));

}


