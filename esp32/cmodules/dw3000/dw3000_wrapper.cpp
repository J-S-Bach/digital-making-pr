#include "dw3000_wrapper.h"
#include "DW3000.h"

extern "C" {

// Just Forwarding. For docs, see h file.

// Most important functions according to docs
// (https://github.com/Fhilb/DW3000_Arduino)
void begin() { return DW3000Class::begin(); };
void init() { return DW3000Class::init(); };
void hardReset() { return DW3000Class::hardReset(); };
void setupGPIO() { return DW3000Class::setupGPIO(); };
void pullLEDHigh(int led) { return DW3000Class::pullLEDHigh(led); };
void pullLEDLow(int led) { return DW3000Class::pullLEDLow(led); };
int ds_processRTInfo(int t_roundA, int t_replyA, int t_roundB, int t_replyB,
                     int clk_offset) {
  return DW3000Class::ds_processRTInfo(t_roundA, t_replyA, t_roundB, t_replyB,
                                       clk_offset);
};

// Uses all the given parameters to calculate the distance between the chips
// after doing a double-sided ranging. Returns a time value that is in
// DW3000 custom units of ~15.65ps per unit.

// Should be processed by convertToCM() to get a usable result.
bool checkSPI() { return DW3000Class::checkSPI(); };

// Used in examples
bool checkForIDLE() { return DW3000Class::checkForIDLE(); };

// Used best by inputting return values of ds_processRTInfo
double convertToCM(int dw3000_ps_units) {
  return DW3000Class::convertToCM(dw3000_ps_units);
};

// Now there are exposed functions, but they are not mentioned as "important" in
// docuementation. The examples use them anyway, so we are mirroring them too.

int *getConfig() { return DW3000Class::config; };

// Chip Setup
void spiSelect(uint8_t cs) { return DW3000Class::spiSelect(cs); };

void writeSysConfig() { return DW3000Class::writeSysConfig(); };
void configureAsTX() { return DW3000Class::configureAsTX(); };

// Double-Sided Ranging
void ds_sendFrame(int stage) { return DW3000Class::ds_sendFrame(stage); };
void ds_sendRTInfo(int t_roundB, int t_replyB) {
  return DW3000Class::ds_sendRTInfo(t_roundB, t_replyB);
};
int ds_getStage() { return DW3000Class::ds_getStage(); };
bool ds_isErrorFrame() { return DW3000Class::ds_isErrorFrame(); };
void ds_sendErrorFrame() { return DW3000Class::ds_sendErrorFrame(); };

// Radio Settings
void setChannel(uint8_t data) { return DW3000Class::setChannel(data); };
void setPreambleLength(uint8_t data) {
  return DW3000Class::setPreambleLength(data);
};
void setPreambleCode(uint8_t data) {
  return DW3000Class::setPreambleCode(data);
};
void setPACSize(uint8_t data) { return DW3000Class::setPACSize(data); };
void setDatarate(uint8_t data) { return DW3000Class::setDatarate(data); };
void setPHRMode(uint8_t data) { return DW3000Class::setPHRMode(data); };
void setPHRRate(uint8_t data) { return DW3000Class::setPHRRate(data); };

// Protocol Settings
void setMode(int mode) { return DW3000Class::setMode(mode); };
void setTXFrame(unsigned long long frame_data) {
  return DW3000Class::setTXFrame(frame_data);
};
void setFrameLength(int frame_len) {
  return DW3000Class::setFrameLength(frame_len);
};
void setTXAntennaDelay(int delay) {
  return DW3000Class::setTXAntennaDelay(delay);
};
void setSenderID(int senderID) { return DW3000Class::setSenderID(senderID); };
void setDestinationID(int destID) {
  return DW3000Class::setDestinationID(destID);
};

// Status Checks
int receivedFrameSucc() { return DW3000Class::receivedFrameSucc(); };
int sentFrameSucc() { return DW3000Class::sentFrameSucc(); };
int getSenderID() { return DW3000Class::getSenderID(); };
int getDestinationID() { return DW3000Class::getDestinationID(); };

// Radio Analytics
double getSignalStrength() { return DW3000Class::getSignalStrength(); };
double getFirstPathSignalStrength() {
  return DW3000Class::getFirstPathSignalStrength();
};
int getTXAntennaDelay() { return DW3000Class::getTXAntennaDelay(); };
long double getClockOffset(int32_t ext_clock_offset) {
  return DW3000Class::getClockOffset(ext_clock_offset);
};
int getRawClockOffset() { return DW3000Class::getRawClockOffset(); };
float getTempInC() { return DW3000Class::getTempInC(); };

unsigned long long readRXTimestamp() { return DW3000Class::readRXTimestamp(); };
unsigned long long readTXTimestamp() { return DW3000Class::readTXTimestamp(); };

// Chip Interaction
int write(int base, int sub, int data, int data_len) {
  return DW3000Class::write(base, sub, data, data_len);
};

int read(int base, int sub) { return DW3000Class::read(base, sub); };
uint8_t read8bit(int base, int sub) {
  return DW3000Class::read8bit(base, sub);
};
int readOTP(uint8_t addr) { return DW3000Class::readOTP(addr); };

// Delayed Sending Settings
void writeTXDelay(int delay) { return DW3000Class::writeTXDelay(delay); };
void prepareDelayedTX() { return DW3000Class::prepareDelayedTX(); };

// Radio Stage Settings / Transfer and Receive Modes
void delayedTXThenRX() { return DW3000Class::delayedTXThenRX(); };
void delayedTX() { return DW3000Class::delayedTX(); };
void standardTX() { return DW3000Class::standardTX(); };
void standardRX() { return DW3000Class::standardRX(); };
void TXInstantRX() { return DW3000Class::TXInstantRX(); };

// DW3000 Firmware Interaction
void clearSystemStatus() { return DW3000Class::clearSystemStatus(); };

// Calculation and Conversion
void calculateTXRXdiff() { return DW3000Class::calculateTXRXdiff(); };

// Printing
void printRoundTripInformation() {
  return DW3000Class::printRoundTripInformation();
};
void printDouble(double val, unsigned int precision, bool linebreak) {
  return DW3000Class::printDouble(val, precision, linebreak);
};
}
