{
  description = "MicroPython build & esptool development environment for ESP32-C6 with C modules";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    micropython-src = {
      url = "github:micropython/micropython";
      flake = false;
    };
    micropython-lib-src = {
      url = "github:micropython/micropython-lib";
      flake = false;
    };
    microdot-src = {
      url = "github:miguelgrinberg/microdot";
      flake = false;
    };
    berkeley-db-src = {
      url = "github:micropython/berkeley-db-1.xx";
      flake = false;
    };

    # Fetching Makerfabs driver repository with ref specified to prevent 404
    qorvo-dw3000-src = {
      url = "github:Makerfabs/Makerfabs-ESP32-UWB-DW3000?ref=main";
      flake = false;
    };

    esp-idf-nix.url = "github:Cbeck527/esp-idf-nix";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      micropython-src,
      micropython-lib-src,
      berkeley-db-src,
      microdot-src,
      qorvo-dw3000-src,
      esp-idf-nix,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        espDevShell = esp-idf-nix.devShells.${system}.v5;

        run-main = pkgs.writeShellScriptBin "run-main" ''
                    echo "Executing local file main.py on ESP32"

                    if [ -f .env ]; then
                        echo "Loading secrets from .env..."
                        export $(grep -v '^#' .env | xargs)
                    else
                        echo ".env file not found!"
                        return 1
                    fi

                    if [ -n "$WIFI_NAME" ] && [ -n "$WIFI_PASSWORD" ]; then
                      mpremote fs rm config.py 2>/dev/null || true
                      mpremote exec "
          with open('config.py', 'w') as f:
              f.write('WIFI_NAME = \"$WIFI_NAME\"\n')
              f.write('WIFI_PASSWORD = \"$WIFI_PASSWORD\"\n')
          "
                    else
                        echo "WIFI_NAME or WIFI_PASSWORD not set. Skipping config generation."
                    fi

                    mpremote cp -r ./src/* :.
                    mpremote run ./src/main.py
        '';

        run-uwb-test = pkgs.writeShellScriptBin "run-uwb-test" ''
                    echo "Executing local file main.py on ESP32"

                    if [ -f .env ]; then
                        echo "Loading secrets from .env..."
                        export $(grep -v '^#' .env | xargs)
                    else
                        echo ".env file not found!"
                        return 1
                    fi

                    if [ -n "$WIFI_NAME" ] && [ -n "$WIFI_PASSWORD" ]; then
                      mpremote fs rm config.py 2>/dev/null || true
                      mpremote exec "
          with open('config.py', 'w') as f:
              f.write('WIFI_NAME = \"$WIFI_NAME\"\n')
              f.write('WIFI_PASSWORD = \"$WIFI_PASSWORD\"\n')
          "
                    else
                        echo "WIFI_NAME or WIFI_PASSWORD not set. Skipping config generation."
                    fi

                    mpremote cp -r ./uwb-test/* :.
                    mpremote run ./uwb-test/main.py
        '';

        # Build script that automatically stages Decadriver sources and micropython-lib
        build-firmware = pkgs.writeShellScriptBin "build-firmware" ''
            export LOCAL_MPY_DIR="$PWD/build-micropython-src"
            export BUILD_DIR="$PWD/build-ESP32_GENERIC_C6"
            export NCU=$(nproc)

            echo "1. Cleaning previous builds..."
            rm -rf "$LOCAL_MPY_DIR" "$BUILD_DIR"

            echo "2. Staging writable MicroPython source tree & submodules..."
            mkdir -p "$LOCAL_MPY_DIR"
            cp -rT ${micropython-src} "$LOCAL_MPY_DIR"
            chmod -R +w "$LOCAL_MPY_DIR"

            rm -rf "$LOCAL_MPY_DIR/lib/micropython-lib" "$LOCAL_MPY_DIR/lib/berkeley-db-1.xx"
            mkdir -p "$LOCAL_MPY_DIR/lib/micropython-lib" "$LOCAL_MPY_DIR/lib/berkeley-db-1.xx"

            cp -rT ${micropython-lib-src} "$LOCAL_MPY_DIR/lib/micropython-lib"
            cp -rT ${berkeley-db-src} "$LOCAL_MPY_DIR/lib/berkeley-db-1.xx"
            chmod -R +w "$LOCAL_MPY_DIR/lib/"

            echo "3. Forcing USB Serial JTAG REPL configuration..."
            cat << 'EOF' >> "$LOCAL_MPY_DIR/ports/esp32/boards/ESP32_GENERIC_C6/sdkconfig.board"
          CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y
          # CONFIG_ESP_CONSOLE_UART_DEFAULT is not set
          CONFIG_ESP_CONSOLE_SECONDARY_NONE=y
          EOF

            echo "4. Pre-building host mpy-cross..."
            env -i PATH="$PATH" make -C "$LOCAL_MPY_DIR/mpy-cross" -j$NCU

            echo "5. Building ESP32 firmware..."

            idf.py -B "$BUILD_DIR" -C "$LOCAL_MPY_DIR/ports/esp32" fullclean

            idf.py -B "$BUILD_DIR" -C "$LOCAL_MPY_DIR/ports/esp32" \
              -D MICROPY_BOARD=ESP32_GENERIC_C6 \
              -D USER_C_MODULES="${dw3000-mod}/micropython.cmake" \
              merge-bin
        '';
        dm-flash = pkgs.writeShellScriptBin "dm-flash" ''
          BUILD_DIR="./build-ESP32_GENERIC_C6"
          FIRMWARE_BIN="$BUILD_DIR/firmware.bin"
          FALLBACK_BIN="ESP32_GENERIC_C6-20260406-v1.28.0.bin"

          if [ -d "$BUILD_DIR" ] && [ -f "$BUILD_DIR/flash_args" ]; then
              echo "Merging local build artifacts into $FIRMWARE_BIN..."
              (cd "$BUILD_DIR" && esptool --chip esp32c6 merge_bin -o firmware.bin @flash_args)
          fi

          TARGET_BIN=""
          if [ -f "$FIRMWARE_BIN" ]; then
            TARGET_BIN="$FIRMWARE_BIN"
          elif [ -f "$FALLBACK_BIN" ]; then
            TARGET_BIN="$FALLBACK_BIN"
          else
            echo "Error: No firmware image found!"
            exit 1
          fi
            echo "Flashing firmware: $TARGET_BIN"

          esptool --chip esp32c6 --baud 460800 erase_flash
          esptool --chip esp32c6  -b 460800 write_flash -z 0x0 "$TARGET_BIN"

          sleep 3

          install-microdot
          install-aioble
        '';

        esp32Stubs = pkgs.fetchFromGitHub {
          owner = "Josverl";
          repo = "micropython-stubs";
          sparseCheckout = [ "publish/micropython-v1_28_0-esp32-stubs" ];
          rev = "0f3195c43dfbf83c8219782394dfefc003bc3f63";
          sha256 = "sha256-MQlBN6KouZpc7dlSEVHXOmNXz6iXr5bQpDkTGWPCihs=";
        };

        install-aioble = pkgs.writeShellScriptBin "install-aioble" ''
          echo "Installing aioble to connected device..."

          mpremote mip install aioble

          mkdir -p ./typings/aioble/
          cp ${micropython-lib-src}/micropython/bluetooth/aioble/aioble/* ./typings/aioble/
        '';

        install-microdot = pkgs.writeShellScriptBin "install-microdot" ''
          echo "Installing microdot to connected device..."

          mpremote mkdir fs :/lib 2>/dev/null || true
          mpremote fs mkdir :/lib/microdot 2>/dev/null || true
          mpremote fs cp ${microdot-src}/src/microdot/* :lib/microdot

          mkdir -p ./typings/microdot
          cp ${microdot-src}/src/microdot/* ./typings/microdot/
        '';
      in
      {
        devShells.default = pkgs.mkShell {
          # Inherit from ESP-IDF 5.x environment
          inputsFrom = [ espDevShell ];

          env = {
            ESP_IDF_VERSION = "5.5.4";
          };

          buildInputs = with pkgs; [
            # Tools for flashing and remote control
            esptool
            mpremote
            thonny

            # Cross-compilation toolchain for ESP32-C6 (RISC-V architecture)
            cmake
            ninja
            ccache
            git
            python3

            # Local helper scripts
            build-firmware
            dm-flash
            run-main
            run-uwb-test
            install-microdot
            install-aioble
          ];

          shellHook = ''
            echo "MicroPython ESP32-C6 C-Module Development Shell"

            export PYTHONPATH="$PYTHONPATH:${esp32Stubs}/publish/micropython-v1_28_0-esp32-stubs"

            mkdir -p ./typings/
            ln -sf ${esp32Stubs}/publish/micropython-v1_28_0-esp32-stubs/* ./typings/

            if [ -f .env.default ]; then
                rm -f "./typings/config.pyi"
                grep -v '^#' .env.default | grep '=' | cut -d'=' -f1 | while read -r key; do
                key=$(echo "$key" | xargs)
                if [ "$key" = "WIFI_NAME" ]; then
                    echo "WIFI_NAME: str" >> "./typings/config.pyi"
                elif [ "$key" = "WIFI_PASSWORD" ]; then
                    echo "WIFI_PASSWORD: str" >> "./typings/config.pyi"
                elif [ "$key" = "DISCOVERY_PORT" ]; then
                    echo "DISCOVERY_PORT: int | None" >> "./typings/config.pyi"
                else
                    echo "$key: str | None" >> "./typings/config.pyi"
                fi
                done
            else
                echo "No .env.default file found; skipping config.pyi generation."
            fi

            echo "Run 'build-firmware' to build custom MicroPython binaries from './cmodules'"
            echo "Run 'dm-flash' to flash compiled or fallback firmware to a connected device"
          '';
        };
      }
    );
}
