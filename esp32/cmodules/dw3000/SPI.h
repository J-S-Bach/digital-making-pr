#ifndef SPI_H
#define SPI_H

#include <stdint.h>

class SPIClass {
public:
  void begin() {}
  uint8_t transfer(uint8_t data) { return 0; }
};

extern SPIClass SPI;

#endif // SPI_H
