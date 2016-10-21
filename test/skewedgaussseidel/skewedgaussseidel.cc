#include <iostream>

#ifndef MATRIXSIZE
#define MATRIXSIZE 1088
#endif
#ifndef NITERS
#define NITERS 100
#endif
#ifndef TILESIZE
#define TILESIZE 16
#endif
#ifndef EPSILON
#define EPSILON 0.0000001
#endif
#ifndef SCALARTYPE
#define SCALARTYPE double
#endif


// A naive Gauss-Seidel smoother function for comparison purposes
void gaussseidel1d ( unsigned niters, SCALARTYPE a1d[MATRIXSIZE] ) {
	for ( unsigned x = 0; x < niters; ++x ) {
		for ( unsigned y = 1; y < MATRIXSIZE - 1; ++y ) {
			a1d[y] = 0.5*(a1d[y-1] + a1d[y+1]);
		}
	}
}
void gaussseidel2d ( unsigned niters, SCALARTYPE a2d[MATRIXSIZE][MATRIXSIZE] ) {
	for ( unsigned x = 0; x < niters; ++x ) {
		for ( unsigned y = 1; y < MATRIXSIZE - 1; ++y ) {
			for ( unsigned z = 1; z < MATRIXSIZE - 1; ++z ) {
				a2d[y][z] = 0.25*(a2d[y-1][z] + a2d[y+1][z] +
				a2d[y][z-1] + a2d[y][z+1]);
			}
		}
	}
}

typedef SCALARTYPE MatrixType2d[MATRIXSIZE][MATRIXSIZE];
typedef SCALARTYPE MatrixType1d[MATRIXSIZE];


void randomInitMatrix1d ( SCALARTYPE m[MATRIXSIZE] ) {
	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		m[y] = (y%7) ? 1.0f : 0.1f;
		if (y==0) m[y] = 2.0f; // break symmetry to expose bugs
	}
}

void randomInitMatrix2d ( SCALARTYPE m[][MATRIXSIZE] ) {
	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
			m[x][y] = ((x+y)%7) ? 1.0f : 0.1f;
			if (x==0) m[x][y] = 2.0f; // break symmetry to expose bugs
		}
	}
}

SCALARTYPE a1d_ref0[MATRIXSIZE];
SCALARTYPE a2d_ref0[MATRIXSIZE][MATRIXSIZE];

int main ( int argc, char **argv ) {

    randomInitMatrix1d ( a1d_ref0 );
    gaussseidel1d ( NITERS, a1d_ref0 );
    std::cout << "gs1d Done! " << "\n";

    randomInitMatrix2d ( a2d_ref0 );
    gaussseidel2d ( NITERS, a2d_ref0 );
    std::cout << "gs2d Done! " << "\n";
  	
}
