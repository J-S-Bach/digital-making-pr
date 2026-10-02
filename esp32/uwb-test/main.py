import time

import dw3000


def test_uwb():
    print("==========================================")
    print(" Testing DW3000 MicroPython C Module")
    print("==========================================")

    # 1. Check Module Attributes
    print("\n[1] Checking module contents:")
    for item in dir(dw3000):
        print("  -", item)

    # 2. Test Initialization
    print("\n[2] Initializing DW3000 hardware...")
    try:
        dw3000.init()
        print("    --> Success! DW3000 initialized.")
    except Exception as e:
        print("    --> Error during init():", e)
        return

    # 3. Basic Loop Heartbeat Test
    print("\n[3] Running loop test (Press Ctrl+C to stop)...")
    count = 0
    while count < 5:
        count += 1
        print("    Heartbeat tick #{}".format(count))
        time.sleep(1)

    print("\n==========================================")
    print(" All basic tests passed successfully!")
    print("==========================================")


if __name__ == "__main__":
    test_uwb()
