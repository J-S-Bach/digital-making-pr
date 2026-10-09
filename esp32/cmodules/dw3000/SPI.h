#ifndef SPI_H
#define SPI_H

#include "driver/spi_master.h"
#include <stdint.h>

class SPIClass {
private:
  spi_device_handle_t spi;
  bool initialized = false;

public:
  void begin();
  uint8_t transfer(uint8_t data);
};

extern SPIClass SPI;

#endif
