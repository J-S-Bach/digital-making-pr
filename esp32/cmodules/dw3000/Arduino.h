#ifndef ARDUINO_H
#define ARDUINO_H

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

// C linkage for low-level functions
#ifdef __cplusplus
extern "C" {
#endif

inline void pinMode(uint8_t pin, uint8_t mode) {}
inline void digitalWrite(uint8_t pin, uint8_t val) {}
inline void delay(unsigned long ms) {}

#ifdef __cplusplus
}
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

#endif // ARDUINO_H
