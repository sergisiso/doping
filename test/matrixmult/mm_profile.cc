#include <time.h>
#include <iostream>
#include <time.h>

#define MATRIXSIZE 1088
#define TILESIZE 144
#define SCALARTYPE double

// A naive matrix multiply function for comparison purposes
void matrixMult ( SCALARTYPE a[][MATRIXSIZE], SCALARTYPE b[][MATRIXSIZE], SCALARTYPE c[][MATRIXSIZE] ) {
//  --------- CODE TRANSFORMED BY JAKE ----------
//  --------- Old version: ----------
//	for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
//		for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
//			for ( unsigned z = 0; z < MATRIXSIZE; ++z ) {
//				c[x][y] += a[x][z] * b[z][y];
//			}
//		}
//	}
//  --------- New version: ----------
time_t JAKEend, JAKElast;
JAKEend = time(NULL) + 2;
JAKElast = time(NULL);
unsigned x = 0 ;
for(; ( x < MATRIXSIZE  ) && JAKElast < JAKEend ; ++ x )
  { for ( unsigned y = 0 ; y < MATRIXSIZE ; ++ y ) { for ( unsigned z = 0 ; z < MATRIXSIZE ; ++ z ) { c [ x ] [ y ] += a [ x ] [ z ] * b [ z ] [ y ] ; } } JAKElast = time(NULL); }
float JAKEprogress = float(x)/MATRIXSIZE;
std::cout << "Loop at interation" << x << "(" << JAKEprogress << "%)" << std::endl ;
std::cout << "Loop total time estimation:" << 2/JAKEprogress << "secs" << std::endl ;
for(; x < MATRIXSIZE ; ++ x )
  { for ( unsigned y = 0 ; y < MATRIXSIZE ; ++ y ) { for ( unsigned z = 0 ; z < MATRIXSIZE ; ++ z ) { c [ x ] [ y ] += a [ x ] [ z ] * b [ z ] [ y ] ; } } }
}

void randomInitMatrix ( SCALARTYPE m[][MATRIXSIZE] ) {
	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
			m[x][y] = 1.0f;
		}
	}
}

void zeroMatrix ( SCALARTYPE m[][MATRIXSIZE] ) {
	for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
		for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
			m[x][y] = 0.0f;
		}
	}
}

SCALARTYPE a[MATRIXSIZE][MATRIXSIZE], b[MATRIXSIZE][MATRIXSIZE], c[MATRIXSIZE][MATRIXSIZE];

int main ( int argc, char **argv ) {

	// initialise operand matrices

	randomInitMatrix ( a );
	randomInitMatrix ( b );

	// baseline non-taskgraph version
	zeroMatrix ( c );
    clock_t start = clock();
	matrixMult ( a, b, c );
    clock_t end = clock();
    int msec = (end-start)*1000/ CLOCKS_PER_SEC;
	std::cout << "Matrix multiplication took " << msec/1000 << "." << msec%1000 << "s" << std::endl;
}