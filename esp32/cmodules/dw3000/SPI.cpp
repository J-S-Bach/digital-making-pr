#include "SPI.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include <stdio.h>
// 1. Instantiate the global SPI object required by the Arduino library
SPIClass SPI;

// 2. Implement the hardware initialization
void SPIClass::begin() {
  if (initialized)
    return;

  // Configure the ESP32-C6 Fast SPI Pins (FSPI)
  spi_bus_config_t buscfg = {};
  buscfg.miso_io_num = 2;
  buscfg.mosi_io_num = 7;
  buscfg.sclk_io_num = 6;
  buscfg.quadwp_io_num = -1;
  buscfg.quadhd_io_num = -1;
  buscfg.max_transfer_sz = 4096;

  // Initialize SPI bus on SPI2_HOST
  esp_err_t ret = spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO);
  if (ret != ESP_OK) {
    printf("[ERROR] Failed to initialize SPI bus\n");
    return;
  }

  // Configure the device connection
  spi_device_interface_config_t devcfg = {};
  devcfg.clock_speed_hz = 2000000; // 2 MHz for stable init
  devcfg.mode = 0;                 // SPI Mode 0
  devcfg.spics_io_num = -1;        // CS is handled manually by DW3000 library
  devcfg.queue_size = 1;

  // Attach the device to the SPI bus
  ret = spi_bus_add_device(SPI2_HOST, &devcfg, &spi);
  if (ret != ESP_OK) {
    printf("[ERROR] Failed to add SPI device\n");
    return;
  }

  initialized = true;
  printf("[INFO] ESP-IDF Hardware SPI Initialized\n");
}

uint8_t SPIClass::transfer(uint8_t data) {
  ESP_LOGI("TAG", "Tx: %02X | Rx: %02X", data);
  if (!initialized)
    return 0;

  uint8_t rx_data = 0;
  spi_transaction_t t = {};
  t.length = 8;           // 8 bits to transfer
  t.tx_buffer = &data;    // Send buffer
  t.rx_buffer = &rx_data; // Receive buffer

  // Execute synchronous transaction to clock the data
  spi_device_polling_transmit(spi, &t);

  return rx_data;
}
