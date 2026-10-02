#include "dw3000_wrapper.h"
#include "DW3000.h"

extern "C" {

int dw3000_init_c(int rst_pin, int ss_pin, int irq_pin) {
  // If your DW3000 class uses pre-configured pins or hardcoded pin definitions:
  DW3000Class::begin();
  DW3000Class::init();
  return 0;
}

float dw3000_read_distance_c(void) {
  // Replace this with your driver's actual distance/ranging call or raw
  // calculation. E.g., if your library uses ds_processRTInfo or similar:
  return 0.0f;
}
}
