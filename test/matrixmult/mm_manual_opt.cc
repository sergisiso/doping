#include <iostream>
#include <stdlib.h>
#include <time.h>
#include <sstream>


void matrixMult ( double *__restrict__ a, double *__restrict__ b, double *__restrict__ c, int MATRIXSIZE) {
	for ( unsigned x = 0; x < 1000; ++x ) {
		for ( unsigned y = 0; y < 1000; ++y ) {
			for ( unsigned z = 0; z < 1000; ++z ) {
				c[x * 1000 + y] += a[x * 1000 + z] * b[z * 1000 + y];
			}
		}
	}
}

void randomInitMatrix ( double *m, int MATRIXSIZE ) {
	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
			m[x * MATRIXSIZE + y] = 1.0f;
		}
	}
}

void zeroMatrix ( double *m, int MATRIXSIZE ) {
	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
			m[x * MATRIXSIZE + y] = 0.0f;
		}
	}
}

int sumAll (double *m, int MATRIXSIZE){

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
    if (argc != 2){
        std::cerr << "Invalid number of parameters" << std::endl;
        return -1;
    }
    std::istringstream ss(argv[1]);
    int N;
    N = atoi(argv[1]);

    std::cout << "N is " << N << std::endl;

    double * a = (double*)malloc(N*N*sizeof(double));
    double * b = (double*)malloc(N*N*sizeof(double));
    double * c = (double*)malloc(N*N*sizeof(double));

	// initialise operand matrices
	randomInitMatrix ( a, N);
	randomInitMatrix ( b, N);

	// baseline non-taskgraph version
	zeroMatrix ( c, N);
    clock_t start = clock();
	matrixMult ( a, b, c, N);
    clock_t end = clock();
    int msec = (end-start)*1000/ CLOCKS_PER_SEC;
	std::cout << "Matrix multiplication took " << msec/1000 << "." << msec%1000 << "s" << std::endl;
    int res = sumAll(c,N);
	std::cout << "Sum of the result = " << res << std::endl;


    free(a);
    free(b);
    free(c);
}
