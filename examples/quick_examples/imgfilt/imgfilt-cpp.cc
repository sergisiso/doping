#include <time.h>
#include <sys/time.h>
#include <stdlib.h>
#include <iostream>
/*
 * Name    : filter
 * Function: Apply a mask to an image. We only filter the central portion
 *
 */

void filter (float *mask, unsigned n, unsigned m, const float *input, float *output, unsigned p, unsigned q)
{
	float    sum;
	unsigned half_n = (n/2);
	unsigned half_m = (m/2);

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

float average (float *m, unsigned size){

    float sum = 0;
	for ( unsigned x = 0; x < size; ++x ) {
        for ( unsigned y = 0; y < size; ++y ) {
			sum = m[x * size + y];
		}
	}
    return sum/(size*size);

}

int main (int argc, char **argv) {

    unsigned img_size;
    unsigned msk_size;
    unsigned num_masks;
    unsigned num_images;

    // Get array size from first argument
    if (argc == 2){
        num_masks = atoi(argv[1]);
        num_images = 1;
        img_size = 1024;
        msk_size = 8;
    }else if(argc == 5){
    	num_masks = atoi(argv[1]);
    	num_images = atoi(argv[2]);
    	img_size = atoi(argv[3]);
    	msk_size = atoi(argv[4]);
    }else{
        std::cerr << "Invalid number of parameters" << std::endl;
        return -1;
    }

    float * im1 = new float[img_size*img_size];
    float * im2 = new float[img_size*img_size];
    float * msk = new float[msk_size*msk_size];
    double t;

    srand(1);

    // Generate a random image
    srand48 (time (NULL));
    for (unsigned i = 0; i < img_size; i++){
        for (unsigned j = 0; j < img_size; j++){
            float r = (float)rand()/(float)(RAND_MAX) * 255 ;
			im1[i * img_size + j] = r;
			im2[i * img_size + j] = r;
        }
    }

    // Generate NUM_MASKS masks and filter im1 with them
    for (unsigned n = 0; n < num_masks; n++) {
	// Generate a mask
	for (unsigned i = 0; i < msk_size; i++)
	    for (unsigned j = 0; j < msk_size; j++)
		msk[i * msk_size + j] = (float)rand()/(float)(RAND_MAX) * 2;

	// Filter the image
	for (unsigned m = 0; m < num_images; m++)
	    filter ((float *) msk, msk_size, msk_size, (float *) im1, (float *) im2, img_size, img_size);
    }

    std::cout << "Original image average: " << average((float *)im1, img_size) << "\n";
    std::cout << "Filtered image average: " << average((float *)im2, img_size) << "\n";

    delete[] im1;
    delete[] im2;
    delete[] msk;
}
