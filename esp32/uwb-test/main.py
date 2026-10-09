import dw3000
import machine

PIN_CS = 16
PIN_RST = 4

print("--- Starting DW3000 Raw C++ Test ---")

# 1. Pull CS High
cs = machine.Pin(PIN_CS, machine.Pin.OUT)
cs.value(1)

# 2. Hardware Reset via GPIO 4
print("Resetting chip...")
rst = machine.Pin(PIN_RST, machine.Pin.OUT)
rst.value(0)
time.sleep_ms(10)
rst.init(machine.Pin.IN)  # Let pull-up pull it high
time.sleep_ms(200)  # 200ms stabilization delay

# 3. Hand everything over to C++
print("Passing control to C++ library...")
dw3000.spiSelect(PIN_CS)
dw3000.begin()

print("Checking SPI connection...")
if dw3000.checkSPI():
    print("[SUCCESS] Connected to DW3000!")
else:
    print("[FAILED] SPI check failed. Check your MISO/MOSI/SCK physical wiring.")
