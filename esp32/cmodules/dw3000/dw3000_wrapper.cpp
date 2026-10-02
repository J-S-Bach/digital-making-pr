#include "dw3000_wrapper.h"
#include "DW3000_Arduino/DW3000/src/DW3000.h"
extern "C" {
int dw3000_init_c(int rst_pin, int ss_pin, int irq_pin) {
  DW3000.begin(rst_pin, ss_pin, irq_pin);
  return 0;
}
float dw3000_read_distance_c(void) { return DW3000.getDistance(); }
}
