#ifndef ARDUINO_H
#define ARDUINO_H

#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <math.h>
#include <stdint.h>
#include <stdio.h>

// Pin Modes and States
#define INPUT 0x0
#define OUTPUT 0x1
#define INPUT_PULLUP 0x2

#define LOW 0x0
#define HIGH 0x1

// Print Base Formats
#define DEC 10
#define HEX 16
#define OCT 8
#define BIN 2

// Arduino Bit Manipulation Macros
#ifndef bitSet
#define bitSet(value, bit) ((value) |= (1UL << (bit)))
#endif

#ifndef bitClear
#define bitClear(value, bit) ((value) &= ~(1UL << (bit)))
#endif

#ifndef bitRead
#define bitRead(value, bit) (((value) >> (bit)) & 0x01)
#endif

#ifndef bitWrite
#define bitWrite(value, bit, bitvalue)                                         \
  ((bitvalue) ? bitSet(value, bit) : bitClear(value, bit))
#endif

// Serial Mock mapping to stdout
class HardwareSerial {
public:
  void print(const char *msg) { printf("%s", msg); }
  void print(int val, int base = DEC) { printf("%d", val); }
  void println(const char *msg = "") { printf("%s\n", msg); }
  void println(int val, int base = DEC) { printf("%d\n", val); }
};

extern HardwareSerial Serial;

// C linkage for low-level Arduino functions mapped to ESP-IDF
#ifdef __cplusplus
extern "C" {
#endif

inline void pinMode(uint8_t pin, uint8_t mode) {
  gpio_reset_pin((gpio_num_t)pin);
  if (mode == OUTPUT) {
    gpio_set_direction((gpio_num_t)pin, GPIO_MODE_OUTPUT);
  } else if (mode == INPUT_PULLUP) {
    gpio_set_direction((gpio_num_t)pin, GPIO_MODE_INPUT);
    gpio_set_pull_mode((gpio_num_t)pin, GPIO_PULLUP_ONLY);
  } else {
    gpio_set_direction((gpio_num_t)pin, GPIO_MODE_INPUT);
    gpio_set_pull_mode((gpio_num_t)pin, GPIO_FLOATING);
  }
}

inline void digitalWrite(uint8_t pin, uint8_t val) {
  gpio_set_level((gpio_num_t)pin, val);
}

inline int digitalRead(uint8_t pin) { return gpio_get_level((gpio_num_t)pin); }

inline void delay(unsigned long ms) { vTaskDelay(pdMS_TO_TICKS(ms)); }

#ifdef __cplusplus
}
#endif

#endif // ARDUINO_H
