#include <TaskGraph>
#include <iostream>
#include <time.h>

using namespace tg;
#define MATRIXSIZE 512
#define TILESIZE 144
#define SCALARTYPE double

// A naive matrix multiply function for comparison purposes
/*void matrixMult ( SCALARTYPE a[][MATRIXSIZE], SCALARTYPE b[][MATRIXSIZE], SCALARTYPE c[][MATRIXSIZE] ) {
	for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
		for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
			for ( unsigned z = 0; z < MATRIXSIZE; ++z ) {
				c[x][y] += a[x][z] * b[z][y];
			}
		}
	}
}
*/

void matrixMult ( SCALARTYPE a[MATRIXSIZE][MATRIXSIZE], SCALARTYPE b[MATRIXSIZE][MATRIXSIZE], SCALARTYPE c[MATRIXSIZE][MATRIXSIZE] ) {
//  --------- CODE TRANSFORMED BY JAKE ----------
//  --------- Old version: ----------
//	for ( unsigned x = 0; x < MATRIXSIZE; ++x ) {
//		for ( unsigned y = 0; y < MATRIXSIZE; ++y ) {
//			for ( unsigned z = 0; z < MATRIXSIZE; ++z ) {
//				c[x][y] += a[x][z] * b[z][y];
//			}
//		}
//	}
//  --------- TG version: ----------
typedef SCALARTYPE MatrixType[MATRIXSIZE][MATRIXSIZE];
typedef tg::TaskGraph<void , SCALARTYPE[MATRIXSIZE][MATRIXSIZE] , SCALARTYPE[MATRIXSIZE][MATRIXSIZE] , SCALARTYPE[MATRIXSIZE][MATRIXSIZE] > tgtype;
tgtype tg0;

taskgraph(tgtype, tg0,  tuple3( a , c , b  ) ) {
  tVar( unsigned, y);
  tVar( unsigned, x);
  tVar( unsigned, z);
  tFor( x, 0,(MATRIXSIZE - 1)){
    tFor( y, 0,(MATRIXSIZE - 1)){
      tFor( z, 0,(MATRIXSIZE - 1)){
        c [ x ] [ y ] += a [ x ] [ z ] * b [ z ] [ y ] ;
      }
    }
  }
}
tg0.compile( tg::GCC);
tg0.execute( a , c , b  );
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