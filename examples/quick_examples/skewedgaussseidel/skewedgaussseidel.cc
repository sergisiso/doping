#include <iostream>
#include <stdlib.h>

#ifndef SCALARTYPE
#define SCALARTYPE double
#endif


// A naive Gauss-Seidel smoother function for comparison purposes
void gaussseidel1d ( unsigned niters, int MATRIXSIZE, SCALARTYPE * a1d ) {
	for ( unsigned x = 0; x < niters; ++x ) {
		for ( unsigned y = 1; y < MATRIXSIZE - 1; ++y ) {
			a1d[y] = 0.5*(a1d[y-1] + a1d[y+1]);
		}
	}
}
void gaussseidel2d ( unsigned niters, int MATRIXSIZE, SCALARTYPE ** a2d ) {
	for ( unsigned x = 0; x < niters; ++x ) {
		for ( unsigned y = 1; y < MATRIXSIZE - 1; ++y ) {
			for ( unsigned z = 1; z < MATRIXSIZE - 1; ++z ) {
				a2d[y][z] = 0.25*(a2d[y-1][z] + a2d[y+1][z] +
				a2d[y][z-1] + a2d[y][z+1]);
			}
		}
	}
}


void randomInitMatrix1d ( int MATRIXSIZE, SCALARTYPE * m ) {
	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		m[y] = (y%7) ? 1.0f : 0.1f;
		if (y==0) m[y] = 2.0f; // break symmetry to expose bugs
	}
}

void randomInitMatrix2d ( int MATRIXSIZE, SCALARTYPE ** m ) {
	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
			m[x][y] = ((x+y)%7) ? 1.0f : 0.1f;
			if (x==0) m[x][y] = 2.0f; // break symmetry to expose bugs
		}
	}
}

SCALARTYPE sumAll1( int MATRIXSIZE, SCALARTYPE * m){

    SCALARTYPE sum = 0;

	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
        sum += m[y];
	}
    return sum;
}

SCALARTYPE sumAll2( int MATRIXSIZE, SCALARTYPE ** m){

    SCALARTYPE sum = 0;

	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
            sum += m[x][y];
		}
	}
    return sum;
}


int main ( int argc, char **argv ) {

    int matrix_size;
    int niters;
    double epsilon;

    // Get array size from first argument
    if (argc == 2){
        niters = atoi(argv[1]);
        matrix_size = 1088*2;
        epsilon = 0.0000001;
    }else if(argc == 5){
    	niters = atoi(argv[1]);
    	matrix_size = atoi(argv[2]);
    	epsilon = atof(argv[3]);
    }else{
        std::cerr << "Invalid number of parameters" << std::endl;
        return -1;
    }
    SCALARTYPE * a1d_ref0 = new SCALARTYPE[matrix_size];
    SCALARTYPE ** a2d_ref0 = new SCALARTYPE*[matrix_size];
    for(int i = 0; i < matrix_size; i++)
            a2d_ref0[i] = new SCALARTYPE[matrix_size];


    randomInitMatrix1d ( matrix_size, a1d_ref0 );
    std::cout << "gs1d Init: " << sumAll1( matrix_size,a1d_ref0) << "\n";
    gaussseidel1d ( niters, matrix_size, a1d_ref0 );
    std::cout << "gs1d Done: " << sumAll1( matrix_size,a1d_ref0) << "\n";

    randomInitMatrix2d ( matrix_size, a2d_ref0 );
    std::cout << "gs2d Init: " << sumAll2( matrix_size,a2d_ref0) << "\n";
    gaussseidel2d ( niters, matrix_size, a2d_ref0 );
    std::cout << "gs2d Done: " << sumAll2( matrix_size,a2d_ref0) << "\n";
  	
}
