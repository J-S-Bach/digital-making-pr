#ifndef DW3000_WRAPPER_H
#define DW3000_WRAPPER_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// These are the functions that are available and should be used according to
// the documentation (https://github.com/Fhilb/DW3000_Arduino)

void begin();

// Has to be called before anything else is done with the library. The
// method configures the SPI bus to communicate with the DW3000 chip.
void init();

// Checks the connection towards the chip by reading known data from the
// chip and comparing it to what the data should look like. Soft resets the
// DW3000 chip and configures the chip.
void hardReset();

// Physically resets the DW3000 chip by pulling the reset line low. This is
// useful if the chip didn't get disconnected from power to ensure that no
// registers are still set.
void setupGPIO();

// Configures the GPIO pins on the DW3000 chip. These pins can be used to
// light some status LEDs.
void pullLEDHigh(int led);

// Lights a LED. 0-2 are valid values and control a different LED each.
void pullLEDLow(int led);

// Shuts off a LED. 0-2 are valid values and control a different LED each.
int ds_processRTInfo(int t_roundA, int t_replyA, int t_roundB, int t_replyB,
                     int clk_offset);

// Uses all the given parameters to calculate the distance between the chips
// after doing a double-sided ranging. Returns a time value that is in
// DW3000 custom units of ~15.65ps per unit.

// Should be processed by convertToCM() to get a usable result.
bool checkSPI();

// Used in examples
bool checkForIDLE();

// Used best by inputting return values of ds_processRTInfo
double convertToCM(int dw3000_ps_units);

// Now there are exposed functions, but they are not mentioned as "important" in
// docuementation. The examples use them anyway, so we are mirroring them too.

int *getConfig();

// Chip Setup
void spiSelect(uint8_t cs);

void writeSysConfig();
void configureAsTX();

// Double-Sided Ranging
void ds_sendFrame(int stage);
void ds_sendRTInfo(int t_roundB, int t_replyB);
int ds_getStage();
bool ds_isErrorFrame();
void ds_sendErrorFrame();

// Radio Settings
void setChannel(uint8_t data);
void setPreambleLength(uint8_t data);
void setPreambleCode(uint8_t data);
void setPACSize(uint8_t data);
void setDatarate(uint8_t data);
void setPHRMode(uint8_t data);
void setPHRRate(uint8_t data);

// Protocol Settings
void setMode(int mode);
void setTXFrame(unsigned long long frame_data);
void setFrameLength(int frame_len);
void setTXAntennaDelay(int delay);
void setSenderID(int senderID);
void setDestinationID(int destID);

// Status Checks
int receivedFrameSucc();
int sentFrameSucc();
int getSenderID();
int getDestinationID();

// Radio Analytics
double getSignalStrength();
double getFirstPathSignalStrength();
int getTXAntennaDelay();
long double getClockOffset(int32_t ext_clock_offset);
int getRawClockOffset();
float getTempInC();

unsigned long long readRXTimestamp();
unsigned long long readTXTimestamp();

// Chip Interaction
int write(int base, int sub, int data, int data_len);

int read(int base, int sub);
uint8_t read8bit(int base, int sub);
int readOTP(uint8_t addr);

// Delayed Sending Settings
void writeTXDelay(int delay);
void prepareDelayedTX();

// Radio Stage Settings / Transfer and Receive Modes
void delayedTXThenRX();
void delayedTX();
void standardTX();
void standardRX();
void TXInstantRX();

// DW3000 Firmware Interaction
void clearSystemStatus();

// Calculation and Conversion
void calculateTXRXdiff();

// Printing
void printRoundTripInformation();
void printDouble(double val, unsigned int precision, bool linebreak);

#ifdef __cplusplus
}
#endif

#endif // DW3000_WRAPPER_H
