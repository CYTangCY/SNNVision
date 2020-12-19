/* main
 * This is a custom main for optimization testing.
 * Chen-Fu Yeh, 19/10/09
 */

#include "iq_network.h"
#include "iz_network.h"
#include "lif_network.h"
#include <stdio.h>
#include <random>
#include <time.h>

using namespace std;

int main(void)
{
    clock_t start, end;
    double time_total;

    int i;
    lif_network network_lif("../inputs/neuronParameter_LIF.txt", "../inputs/Connection_Table_LIF.txt");
    //lif_network network_lif("neuron_lif.txt", "table_lif.txt");
    //int iq_num_neurons = network_iq.num_neurons();
    int lif_num_neurons = network_lif.num_neurons();
    start = clock();
    //char filename[] = "iq_output_number.txt";
    char filename[] = "lif_output_number.txt";
    char ICfilename[] = "lif_ICoutput_number.txt";
    char SRfilename[] = "lif_FRoutput_number.txt";
    FILE** fp_p = (FILE**) malloc(sizeof(FILE*) * lif_num_neurons);
    FILE** fp_i = (FILE**) malloc(sizeof(FILE*) * lif_num_neurons);
    FILE** fp_s = (FILE**) malloc(sizeof(FILE*) * lif_num_neurons);
    //FILE** fp_p = (FILE**) malloc(sizeof(FILE*) * iz_num_neurons);
    //FILE** fp_a = (FILE**) malloc(sizeof(FILE*) * iz_num_neurons);

    srand((unsigned) time(NULL));
    //network_iq.set_num_threads(4);
    //network_iz.set_num_threads(4);

    //for(i = 0; i < iq_num_neurons; i++) {
    for(i = 0; i < lif_num_neurons; i++) {
        sprintf(filename, "lif_output_%d.txt", i);
	sprintf(ICfilename, "lif_ICoutput_%d.txt", i);
	sprintf(SRfilename, "lif_FRoutput_%d.txt", i);
        fp_p[i] = fopen(filename, "w");
	fp_i[i] = fopen(ICfilename, "w");
	fp_s[i] = fopen(SRfilename, "w");
        //sprintf(filename, "iz_output_p_%d.txt", i);
        //fp_p[i] = fopen(filename, "w");
        //sprintf(filename, "iz_output_a_%d.txt", i);
        //fp_a[i] = fopen(filename, "w");
        //network_iq.set_biascurrent(i, 4);
        //network_iz.set_biascurrent(i, 4);
    }

    int steps, idx;
    float bias;
    //printf("How many timesteps do you want?\n");
    scanf(" %d", &steps);
    while(steps >= 0) {
        //printf("steps: %d\n", steps);

        //printf("Neuron to insert bias current:\n");
        scanf(" %d", &idx);
        while(idx >= 0) {
            //printf("How much current do you want to insert?\n");
            scanf(" %f", &bias);
            //network_iq.set_biascurrent(idx, bias);
            printf("%f\n", bias);
            network_lif.set_biascurrent(idx, bias);
            //printf("neuron %d is receiving current %d\n", idx, bias);

            //printf("Neuron to insert bias current:\n");
            scanf(" %d", &idx);
        }

        //printf("Set complete; sending synapses...\n");
        for(i = 0; i < steps; i++) {
            network_lif.send_synapse();
            network_lif.printfile(fp_p, fp_i, fp_s);
            //network_iz.send_synapse();
            //network_iz.printfile(fp_p, fp_a);
        }
        //printf("Synapse OK. Waiting for next period...\n");
        //printf("How many timesteps do you want?\n");
        scanf(" %d", &steps);
    }

    /* set bias current */
    //network_iq.set_biascurrent(0, 3);

    /* send synapse */
    /*
    for(i = 0; i < 2000; i++) {
        //printf("%d\n", i);
        network_iq.send_synapse();
        //network_iz.send_synapse();
        network_iq.printfile(fp);
        //network_iz.printfile(fp_p, fp_a);
    }
    */

    //printf("Simulation finished. Quitting...\n");

    //for(i = 0; i < iq_num_neurons; i++) {
    for(i = 0; i < lif_num_neurons; i++) {
        fclose(fp_p[i]);
	fclose(fp_i[i]);
	fclose(fp_s[i]);
        //fclose(fp_p[i]);
        //fclose(fp_a[i]);
    }
    free(fp_p);
    free(fp_i);
    free(fp_s);
    //free(fp_p);
    //free(fp_a);
    end = clock();
    time_total = (double) (end - start) / CLOCKS_PER_SEC;
    //printf("total execution time: %f sec\n", time_total);
    return 0;
}

