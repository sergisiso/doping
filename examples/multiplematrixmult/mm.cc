#include <iostream>
#include <stdlib.h>
#include <time.h>
#include <sstream>


void do_x_matrixMult (unsigned num, double *a, double *b, double *c, unsigned MATRIXSIZE) {
    for ( unsigned n = 0; n < num; n++){
	    for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
		    for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
			    for ( unsigned z = 0; z < MATRIXSIZE; ++z ) {
				    c[x * MATRIXSIZE + y] += a[x * MATRIXSIZE + z] * b[z * MATRIXSIZE + y];
			    }
		    }
	    }
    }
}

void randomInitMatrix ( double *m, unsigned MATRIXSIZE ) {
	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
			m[x * MATRIXSIZE + y] = 1.0f;
		}
	}
}

void zeroMatrix ( double *m, unsigned MATRIXSIZE ) {
	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
			m[x * MATRIXSIZE + y] = 0.0f;
		}
	}
}

int sumAll (double *m, unsigned MATRIXSIZE){

    int sum = 0;
    for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
			sum = m[x * MATRIXSIZE + y];
		}
	}
    return sum;

}

int main ( int argc, char **argv ) {


    // Get array size from first argument
    if (argc != 3){
        std::cerr << "Invalid number of parameters" << std::endl;
        return -1;
    }
    int N;
    N = atoi(argv[1]);
    int rep;
    rep = atoi(argv[2]);

    std::cout << "N is " << N << std::endl;

    double * a = (double*)malloc(N*N*sizeof(double));
    double * b = (double*)malloc(N*N*sizeof(double));
    double * c = (double*)malloc(N*N*sizeof(double));

	// initialise operand matrices
	randomInitMatrix ( a, N);
	randomInitMatrix ( b, N);

	// baseline non-taskgraph version
	zeroMatrix ( c, N);
    //clock_t start = clock();
	do_x_matrixMult (rep, a, b, c, N);
    //clock_t end = clock();
    //int msec = (end-start)*1000/ CLOCKS_PER_SEC;
    //std::cout << "Matrix multiplication took " << msec/1000 << "." << msec%1000 << "s" << std::endl;
    int res = sumAll(c,N);
	std::cout << "Sum of the result = " << res << std::endl;


    free(a);
    free(b);
    free(c);
}
