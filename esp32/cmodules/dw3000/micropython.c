// AI Generated based on dw3000_wrapper.h (which was in turn just copying
// headers from https://github.com/Fhilb/DW3000_Arduino)
#include "dw3000_wrapper.h"
#include "py/obj.h"
#include "py/objint.h"
#include "py/runtime.h"

// --------------------------------------------------------------------------
// Basic 0-argument void functions
// --------------------------------------------------------------------------

#define MAKE_VOID_FUNC_0(func_name)                                            \
  static mp_obj_t py_##func_name(void) {                                       \
    func_name();                                                               \
    return mp_const_none;                                                      \
  }                                                                            \
  static MP_DEFINE_CONST_FUN_OBJ_0(py_##func_name##_obj, py_##func_name);

MAKE_VOID_FUNC_0(begin)
MAKE_VOID_FUNC_0(init)
MAKE_VOID_FUNC_0(hardReset)
MAKE_VOID_FUNC_0(setupGPIO)
MAKE_VOID_FUNC_0(writeSysConfig)
MAKE_VOID_FUNC_0(configureAsTX)
MAKE_VOID_FUNC_0(ds_sendErrorFrame)
MAKE_VOID_FUNC_0(prepareDelayedTX)
MAKE_VOID_FUNC_0(delayedTXThenRX)
MAKE_VOID_FUNC_0(delayedTX)
MAKE_VOID_FUNC_0(standardTX)
MAKE_VOID_FUNC_0(standardRX)
MAKE_VOID_FUNC_0(TXInstantRX)
MAKE_VOID_FUNC_0(clearSystemStatus)
MAKE_VOID_FUNC_0(calculateTXRXdiff)
MAKE_VOID_FUNC_0(printRoundTripInformation)

// --------------------------------------------------------------------------
// 0-argument functions with return values
// --------------------------------------------------------------------------

static mp_obj_t py_checkSPI(void) { return mp_obj_new_bool(checkSPI()); }
static MP_DEFINE_CONST_FUN_OBJ_0(py_checkSPI_obj, py_checkSPI);

static mp_obj_t py_checkForIDLE(void) {
  return mp_obj_new_bool(checkForIDLE());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_checkForIDLE_obj, py_checkForIDLE);

// Assuming DW3000Class::config is always an array of 9 ints based on previous
// context
static mp_obj_t py_getConfig(void) {
  int *config_ptr = getConfig();
  mp_obj_t tuple_items[9];

  for (int i = 0; i < 9; i++) {
    tuple_items[i] = mp_obj_new_int(config_ptr[i]);
  }

  return mp_obj_new_tuple(9, tuple_items);
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_getConfig_obj, py_getConfig);

static mp_obj_t py_ds_getStage(void) { return mp_obj_new_int(ds_getStage()); }
static MP_DEFINE_CONST_FUN_OBJ_0(py_ds_getStage_obj, py_ds_getStage);

static mp_obj_t py_ds_isErrorFrame(void) {
  return mp_obj_new_bool(ds_isErrorFrame());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_ds_isErrorFrame_obj, py_ds_isErrorFrame);

static mp_obj_t py_receivedFrameSucc(void) {
  return mp_obj_new_int(receivedFrameSucc());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_receivedFrameSucc_obj,
                                 py_receivedFrameSucc);

static mp_obj_t py_sentFrameSucc(void) {
  return mp_obj_new_int(sentFrameSucc());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_sentFrameSucc_obj, py_sentFrameSucc);

static mp_obj_t py_getSenderID(void) { return mp_obj_new_int(getSenderID()); }
static MP_DEFINE_CONST_FUN_OBJ_0(py_getSenderID_obj, py_getSenderID);

static mp_obj_t py_getDestinationID(void) {
  return mp_obj_new_int(getDestinationID());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_getDestinationID_obj, py_getDestinationID);

static mp_obj_t py_getSignalStrength(void) {
  return mp_obj_new_float((mp_float_t)getSignalStrength());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_getSignalStrength_obj,
                                 py_getSignalStrength);

static mp_obj_t py_getFirstPathSignalStrength(void) {
  return mp_obj_new_float((mp_float_t)getFirstPathSignalStrength());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_getFirstPathSignalStrength_obj,
                                 py_getFirstPathSignalStrength);

static mp_obj_t py_getTXAntennaDelay(void) {
  return mp_obj_new_int(getTXAntennaDelay());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_getTXAntennaDelay_obj,
                                 py_getTXAntennaDelay);

static mp_obj_t py_getRawClockOffset(void) {
  return mp_obj_new_int(getRawClockOffset());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_getRawClockOffset_obj,
                                 py_getRawClockOffset);

static mp_obj_t py_getTempInC(void) {
  return mp_obj_new_float((mp_float_t)getTempInC());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_getTempInC_obj, py_getTempInC);

static mp_obj_t py_readRXTimestamp(void) {
  return mp_obj_new_int_from_ull(readRXTimestamp());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_readRXTimestamp_obj, py_readRXTimestamp);

static mp_obj_t py_readTXTimestamp(void) {
  return mp_obj_new_int_from_ull(readTXTimestamp());
}
static MP_DEFINE_CONST_FUN_OBJ_0(py_readTXTimestamp_obj, py_readTXTimestamp);

// --------------------------------------------------------------------------
// 1-argument functions
// --------------------------------------------------------------------------

#define MAKE_VOID_FUNC_1_INT(func_name)                                        \
  static mp_obj_t py_##func_name(mp_obj_t arg1) {                              \
    func_name(mp_obj_get_int(arg1));                                           \
    return mp_const_none;                                                      \
  }                                                                            \
  static MP_DEFINE_CONST_FUN_OBJ_1(py_##func_name##_obj, py_##func_name);

MAKE_VOID_FUNC_1_INT(pullLEDHigh)
MAKE_VOID_FUNC_1_INT(pullLEDLow)
MAKE_VOID_FUNC_1_INT(spiSelect)
MAKE_VOID_FUNC_1_INT(ds_sendFrame)
MAKE_VOID_FUNC_1_INT(setChannel)
MAKE_VOID_FUNC_1_INT(setPreambleLength)
MAKE_VOID_FUNC_1_INT(setPreambleCode)
MAKE_VOID_FUNC_1_INT(setPACSize)
MAKE_VOID_FUNC_1_INT(setDatarate)
MAKE_VOID_FUNC_1_INT(setPHRMode)
MAKE_VOID_FUNC_1_INT(setPHRRate)
MAKE_VOID_FUNC_1_INT(setMode)
MAKE_VOID_FUNC_1_INT(setFrameLength)
MAKE_VOID_FUNC_1_INT(setTXAntennaDelay)
MAKE_VOID_FUNC_1_INT(setSenderID)
MAKE_VOID_FUNC_1_INT(setDestinationID)

static mp_obj_t py_convertToCM(mp_obj_t arg1) {
  return mp_obj_new_float((mp_float_t)convertToCM(mp_obj_get_int(arg1)));
}
static MP_DEFINE_CONST_FUN_OBJ_1(py_convertToCM_obj, py_convertToCM);

static mp_obj_t py_setTXFrame(mp_obj_t arg1) {
  setTXFrame((unsigned long long)mp_obj_get_uint(arg1));
  return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(py_setTXFrame_obj, py_setTXFrame);

static mp_obj_t py_writeTXDelay(mp_obj_t arg1) {
  writeTXDelay(mp_obj_get_int(arg1));
  return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(py_writeTXDelay_obj, py_writeTXDelay);

static mp_obj_t py_readOTP(mp_obj_t arg1) {
  return mp_obj_new_int(readOTP((uint8_t)mp_obj_get_int(arg1)));
}
static MP_DEFINE_CONST_FUN_OBJ_1(py_readOTP_obj, py_readOTP);

static mp_obj_t py_getClockOffset(mp_obj_t arg1) {
  return mp_obj_new_float(
      (mp_float_t)getClockOffset((int32_t)mp_obj_get_int(arg1)));
}
static MP_DEFINE_CONST_FUN_OBJ_1(py_getClockOffset_obj, py_getClockOffset);

// --------------------------------------------------------------------------
// Multi-argument functions
// --------------------------------------------------------------------------

static mp_obj_t py_ds_processRTInfo(size_t n_args, const mp_obj_t *args) {
  int res = ds_processRTInfo(mp_obj_get_int(args[0]), mp_obj_get_int(args[1]),
                             mp_obj_get_int(args[2]), mp_obj_get_int(args[3]),
                             mp_obj_get_int(args[4]));
  return mp_obj_new_int(res);
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(py_ds_processRTInfo_obj, 5, 5,
                                           py_ds_processRTInfo);

static mp_obj_t py_ds_sendRTInfo(mp_obj_t t_roundB, mp_obj_t t_replyB) {
  ds_sendRTInfo(mp_obj_get_int(t_roundB), mp_obj_get_int(t_replyB));
  return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_2(py_ds_sendRTInfo_obj, py_ds_sendRTInfo);

static mp_obj_t py_read(mp_obj_t base, mp_obj_t sub) {
  return mp_obj_new_int(read(mp_obj_get_int(base), mp_obj_get_int(sub)));
}
static MP_DEFINE_CONST_FUN_OBJ_2(py_read_obj, py_read);

static mp_obj_t py_read8bit(mp_obj_t base, mp_obj_t sub) {
  return mp_obj_new_int(read8bit(mp_obj_get_int(base), mp_obj_get_int(sub)));
}
static MP_DEFINE_CONST_FUN_OBJ_2(py_read8bit_obj, py_read8bit);

static mp_obj_t py_printDouble(mp_obj_t val, mp_obj_t precision,
                               mp_obj_t linebreak) {
  printDouble(mp_obj_get_float(val), (unsigned int)mp_obj_get_int(precision),
              mp_obj_is_true(linebreak));
  return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_3(py_printDouble_obj, py_printDouble);

static mp_obj_t py_write(size_t n_args, const mp_obj_t *args) {
  int res = write(mp_obj_get_int(args[0]), mp_obj_get_int(args[1]),
                  mp_obj_get_int(args[2]), mp_obj_get_int(args[3]));
  return mp_obj_new_int(res);
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(py_write_obj, 4, 4, py_write);

// --------------------------------------------------------------------------
// Module dictionary setup
// --------------------------------------------------------------------------

static const mp_rom_map_elem_t dw3000_module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_dw3000)},

    {MP_ROM_QSTR(MP_QSTR_begin), MP_ROM_PTR(&py_begin_obj)},
    {MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&py_init_obj)},
    {MP_ROM_QSTR(MP_QSTR_hardReset), MP_ROM_PTR(&py_hardReset_obj)},
    {MP_ROM_QSTR(MP_QSTR_setupGPIO), MP_ROM_PTR(&py_setupGPIO_obj)},
    {MP_ROM_QSTR(MP_QSTR_pullLEDHigh), MP_ROM_PTR(&py_pullLEDHigh_obj)},
    {MP_ROM_QSTR(MP_QSTR_pullLEDLow), MP_ROM_PTR(&py_pullLEDLow_obj)},
    {MP_ROM_QSTR(MP_QSTR_ds_processRTInfo),
     MP_ROM_PTR(&py_ds_processRTInfo_obj)},
    {MP_ROM_QSTR(MP_QSTR_checkSPI), MP_ROM_PTR(&py_checkSPI_obj)},
    {MP_ROM_QSTR(MP_QSTR_checkForIDLE), MP_ROM_PTR(&py_checkForIDLE_obj)},
    {MP_ROM_QSTR(MP_QSTR_convertToCM), MP_ROM_PTR(&py_convertToCM_obj)},
    {MP_ROM_QSTR(MP_QSTR_getConfig), MP_ROM_PTR(&py_getConfig_obj)},
    {MP_ROM_QSTR(MP_QSTR_spiSelect), MP_ROM_PTR(&py_spiSelect_obj)},
    {MP_ROM_QSTR(MP_QSTR_writeSysConfig), MP_ROM_PTR(&py_writeSysConfig_obj)},
    {MP_ROM_QSTR(MP_QSTR_configureAsTX), MP_ROM_PTR(&py_configureAsTX_obj)},
    {MP_ROM_QSTR(MP_QSTR_ds_sendFrame), MP_ROM_PTR(&py_ds_sendFrame_obj)},
    {MP_ROM_QSTR(MP_QSTR_ds_sendRTInfo), MP_ROM_PTR(&py_ds_sendRTInfo_obj)},
    {MP_ROM_QSTR(MP_QSTR_ds_getStage), MP_ROM_PTR(&py_ds_getStage_obj)},
    {MP_ROM_QSTR(MP_QSTR_ds_isErrorFrame), MP_ROM_PTR(&py_ds_isErrorFrame_obj)},
    {MP_ROM_QSTR(MP_QSTR_ds_sendErrorFrame),
     MP_ROM_PTR(&py_ds_sendErrorFrame_obj)},
    {MP_ROM_QSTR(MP_QSTR_setChannel), MP_ROM_PTR(&py_setChannel_obj)},
    {MP_ROM_QSTR(MP_QSTR_setPreambleLength),
     MP_ROM_PTR(&py_setPreambleLength_obj)},
    {MP_ROM_QSTR(MP_QSTR_setPreambleCode), MP_ROM_PTR(&py_setPreambleCode_obj)},
    {MP_ROM_QSTR(MP_QSTR_setPACSize), MP_ROM_PTR(&py_setPACSize_obj)},
    {MP_ROM_QSTR(MP_QSTR_setDatarate), MP_ROM_PTR(&py_setDatarate_obj)},
    {MP_ROM_QSTR(MP_QSTR_setPHRMode), MP_ROM_PTR(&py_setPHRMode_obj)},
    {MP_ROM_QSTR(MP_QSTR_setPHRRate), MP_ROM_PTR(&py_setPHRRate_obj)},
    {MP_ROM_QSTR(MP_QSTR_setMode), MP_ROM_PTR(&py_setMode_obj)},
    {MP_ROM_QSTR(MP_QSTR_setTXFrame), MP_ROM_PTR(&py_setTXFrame_obj)},
    {MP_ROM_QSTR(MP_QSTR_setFrameLength), MP_ROM_PTR(&py_setFrameLength_obj)},
    {MP_ROM_QSTR(MP_QSTR_setTXAntennaDelay),
     MP_ROM_PTR(&py_setTXAntennaDelay_obj)},
    {MP_ROM_QSTR(MP_QSTR_setSenderID), MP_ROM_PTR(&py_setSenderID_obj)},
    {MP_ROM_QSTR(MP_QSTR_setDestinationID),
     MP_ROM_PTR(&py_setDestinationID_obj)},
    {MP_ROM_QSTR(MP_QSTR_receivedFrameSucc),
     MP_ROM_PTR(&py_receivedFrameSucc_obj)},
    {MP_ROM_QSTR(MP_QSTR_sentFrameSucc), MP_ROM_PTR(&py_sentFrameSucc_obj)},
    {MP_ROM_QSTR(MP_QSTR_getSenderID), MP_ROM_PTR(&py_getSenderID_obj)},
    {MP_ROM_QSTR(MP_QSTR_getDestinationID),
     MP_ROM_PTR(&py_getDestinationID_obj)},
    {MP_ROM_QSTR(MP_QSTR_getSignalStrength),
     MP_ROM_PTR(&py_getSignalStrength_obj)},
    {MP_ROM_QSTR(MP_QSTR_getFirstPathSignalStrength),
     MP_ROM_PTR(&py_getFirstPathSignalStrength_obj)},
    {MP_ROM_QSTR(MP_QSTR_getTXAntennaDelay),
     MP_ROM_PTR(&py_getTXAntennaDelay_obj)},
    {MP_ROM_QSTR(MP_QSTR_getClockOffset), MP_ROM_PTR(&py_getClockOffset_obj)},
    {MP_ROM_QSTR(MP_QSTR_getRawClockOffset),
     MP_ROM_PTR(&py_getRawClockOffset_obj)},
    {MP_ROM_QSTR(MP_QSTR_getTempInC), MP_ROM_PTR(&py_getTempInC_obj)},
    {MP_ROM_QSTR(MP_QSTR_readRXTimestamp), MP_ROM_PTR(&py_readRXTimestamp_obj)},
    {MP_ROM_QSTR(MP_QSTR_readTXTimestamp), MP_ROM_PTR(&py_readTXTimestamp_obj)},
    {MP_ROM_QSTR(MP_QSTR_write), MP_ROM_PTR(&py_write_obj)},
    {MP_ROM_QSTR(MP_QSTR_read), MP_ROM_PTR(&py_read_obj)},
    {MP_ROM_QSTR(MP_QSTR_read8bit), MP_ROM_PTR(&py_read8bit_obj)},
    {MP_ROM_QSTR(MP_QSTR_readOTP), MP_ROM_PTR(&py_readOTP_obj)},
    {MP_ROM_QSTR(MP_QSTR_writeTXDelay), MP_ROM_PTR(&py_writeTXDelay_obj)},
    {MP_ROM_QSTR(MP_QSTR_prepareDelayedTX),
     MP_ROM_PTR(&py_prepareDelayedTX_obj)},
    {MP_ROM_QSTR(MP_QSTR_delayedTXThenRX), MP_ROM_PTR(&py_delayedTXThenRX_obj)},
    {MP_ROM_QSTR(MP_QSTR_delayedTX), MP_ROM_PTR(&py_delayedTX_obj)},
    {MP_ROM_QSTR(MP_QSTR_standardTX), MP_ROM_PTR(&py_standardTX_obj)},
    {MP_ROM_QSTR(MP_QSTR_standardRX), MP_ROM_PTR(&py_standardRX_obj)},
    {MP_ROM_QSTR(MP_QSTR_TXInstantRX), MP_ROM_PTR(&py_TXInstantRX_obj)},
    {MP_ROM_QSTR(MP_QSTR_clearSystemStatus),
     MP_ROM_PTR(&py_clearSystemStatus_obj)},
    {MP_ROM_QSTR(MP_QSTR_calculateTXRXdiff),
     MP_ROM_PTR(&py_calculateTXRXdiff_obj)},
    {MP_ROM_QSTR(MP_QSTR_printRoundTripInformation),
     MP_ROM_PTR(&py_printRoundTripInformation_obj)},
    {MP_ROM_QSTR(MP_QSTR_printDouble), MP_ROM_PTR(&py_printDouble_obj)},
};

static MP_DEFINE_CONST_DICT(dw3000_module_globals, dw3000_module_globals_table);

const mp_obj_module_t dw3000_user_cmodule = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t *)&dw3000_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_dw3000, dw3000_user_cmodule);
