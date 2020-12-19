#ifndef LIF_NEURON_H
#define LIF_NEURON_H
#include <stdio.h>
#include <stdlib.h>

class lif_neuron
{
public:
    lif_neuron() {};
    bool is_set();
    void set(float g, float rest, float threshold, float reset, float noise);
    void lif_rk4(float external_current);
    void lif_euler(float external_current);
    float potential();
    bool is_firing();
    int spike_count();
    float spike_rate();
    float inputPnoise();

private:
    void funca(float &fa, float &I, const float dtt,
               const float arg);
    int t_neuron;
    float _v = 0;
    float _g, _rest, _threshold, _reset;
    float _noise;
    float VMAX = 255;
    int _spike_count = 0;
    int _r_count = 0, _r_period = 0;
    bool _is_set = false, _is_firing = false;
    float valuenoise;
    float iPn;
    float ISI;
    float Epu;
    float Z;
};

#endif

