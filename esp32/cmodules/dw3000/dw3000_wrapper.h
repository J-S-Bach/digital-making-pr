#ifndef DW3000_WRAPPER_H
#define DW3000_WRAPPER_H
#ifdef __cplusplus
extern "C" {
#endif
int dw3000_init_c(int rst_pin, int ss_pin, int irq_pin);
float dw3000_read_distance_c(void);
#ifdef __cplusplus
}
#endif
#endif
