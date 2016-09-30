#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

double dtime(){
    double tseconds = 0.0;
    struct timeval mytime;
    gettimeofday(&mytime,(struct timezone*)0);
    tseconds = (double)(mytime.tv_sec + mytime.tv_usec*1.0e-6);
    return tseconds;
}

#define ARRAY_SIZE (1024*1024)
#define MAXFLOPS_ITERS 100000000
#define LOOP_COUNT 128
#define FLOPSPERCALC 2

//#define ALIGN_DEC(X) __attribute__((aligned(X)))
//#define ALIGN_BYTES 64

//float fa[ARRAY_SIZE] ALIGN_DEC(ALIGN_BYTES);
//float fb[ARRAY_SIZE] ALIGN_DEC(ALIGN_BYTES;

float fa[ARRAY_SIZE] __attribute__((aligned(64)));
float fb[ARRAY_SIZE] __attribute__((aligned(64)));

int main(){
    int i,j,k;
    double tstart,tstop, ttime;
    double gflops = 0.0;
    float a=1.1;

    printf("Initializing\n");
    for(i=0; i<ARRAY_SIZE; i++){
        fa[i] = (float)i + 0.1;
        fb[i] = (float)i + 0.2;
    }

    printf("Starting compute\n");
    tstart = dtime();

    for(j=0; j<MAXFLOPS_ITERS; j++){
        for(k=0; k< LOOP_COUNT; k++){
            fa[k] = a * fa[k] + fb[k];
        }
    }
    tstop = dtime();

    gflops = (double)(1.0e-9 * LOOP_COUNT * 
             MAXFLOPS_ITERS * FLOPSPERCALC);

    ttime = tstop - tstart;

    if(ttime > 0.0){
        printf("GFlops = %6.3f, Secs = %6.3f,"
               "GFlops per sec = %6.3f\n",
                gflops, ttime, gflops/ttime);

    }
    return 0;
}



