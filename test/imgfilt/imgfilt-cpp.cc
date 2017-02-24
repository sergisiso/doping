#include <time.h>
#include <sys/time.h>
#include <stdlib.h>
#include <iostream>

#define IMG_SIZE	256*5
#define MSK_SIZE	128
#define NUM_MASKS	1
#define NUM_IMAGES	1

/*
 * Name    : filter
 * Function: Apply a mask to an image. We only filter the central portion
 *
 */

void filter (float *mask, unsigned n, unsigned m, const float *input, float *output, unsigned p, unsigned q)
{
	float    sum;
	int half_n = (n/2);
	int half_m = (m/2);

	for (unsigned i = half_n; i < p - half_n; i++) {
		for (unsigned j = half_m; j < q - half_m; j++) {
			sum = 0;

			for (unsigned k = 0; k < n; k++)
				for (unsigned l = 0; l < m; l++)
					sum += input[(i + k - half_n) * q + (j + l - half_m)] * mask[k * m + l];

			output[i * q + j] = sum;
		}
	}
}

double utime () {
  struct timeval tv;

  gettimeofday (&tv, NULL);

  return (tv.tv_sec + double (tv.tv_usec) * 1e-6);
}

float average (float *m, int size){

    float sum = 0;
	for ( unsigned x = 0; x < size; ++x ) {
        for ( unsigned y = 0; y < size; ++y ) {
			sum = m[x * size + y];
		}
	}
    return sum/(size*size);

}

int main (int argc, char **argv) {
	float * im1 = new float[IMG_SIZE*IMG_SIZE];
	float * im2 = new float[IMG_SIZE*IMG_SIZE];
	float * msk = new float[MSK_SIZE*MSK_SIZE];
	double t;

    srand(1);

	// Generate a random image
	srand48 (time (NULL));
	for (unsigned i = 0; i < IMG_SIZE; i++){
		for (unsigned j = 0; j < IMG_SIZE; j++){
            float r = (float)rand()/(float)(RAND_MAX) * 255 ;
			im1[i * IMG_SIZE + j] = r;
			im2[i * IMG_SIZE + j] = r;
        }
    }

	// Generate NUM_MASKS masks and filter im1 with them
	t = -utime ();

	for (unsigned n = 0; n < NUM_MASKS; n++) {
		// Generate a mask
		for (unsigned i = 0; i < MSK_SIZE; i++)
			for (unsigned j = 0; j < MSK_SIZE; j++)
				msk[i * MSK_SIZE + j] = (float)rand()/(float)(RAND_MAX) * 2;

		// Filter the image
		for (unsigned m = 0; m < NUM_IMAGES; m++)
			filter ((float *) msk, MSK_SIZE, MSK_SIZE, (float *) im1, (float *) im2, IMG_SIZE, IMG_SIZE);
    }

	t += utime ();

	std::cout << "Original image average: " << average((float *)im1, IMG_SIZE) << "\n";
	std::cout << "Filtered image average: " << average((float *)im2, IMG_SIZE) << "\n";

	delete[] im1;
	delete[] im2;
	delete[] msk;
}
