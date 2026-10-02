import time

import dw3000

# ESP32-C6 pin configuration for DW3000
RST_PIN = 4
SS_PIN = 5
IRQ_PIN = 6


def test_uwb():
    print("==========================================")
    print(" Testing DW3000 MicroPython C Module")
    print("==========================================")

    # 1. Check Module Attributes
    print("\n[1] Checking module contents:")
    for item in dir(dw3000):
        print("  -", item)

    # 2. Test Initialization with Pin Arguments
    print(
        "\n[2] Initializing DW3000 hardware (RST={}, SS={}, IRQ={})...".format(
            RST_PIN, SS_PIN, IRQ_PIN
        )
    )
    try:
        dw3000.init(RST_PIN, SS_PIN, IRQ_PIN)
        print("    --> Success! DW3000 initialized.")
    except Exception as e:
        print("    --> Error during init():", e)
        return

    # 3. Read Distance Test Loop
    print("\n[3] Reading distance telemetry (Press Ctrl+C to stop)...")
    try:
        for count in range(1, 6):
            dist = dw3000.read_distance()
            print("    Read #{}: Distance = {:.3f} m".format(count, dist))
            time.sleep(1)
    except Exception as e:
        print("    --> Error reading distance:", e)
        return

    print("\n==========================================")
    print(" All basic tests passed successfully!")
    print("==========================================")


if __name__ == "__main__":
    test_uwb()
