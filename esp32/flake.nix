{
  description = "Esptool environment for ESP32. This is basically the same thing as arduino-cli, but in python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    micropython-lib-src = {
      url = "github:micropython/micropython-lib";
      flake = false;
    };
    microdot-src = {
      url = "github:miguelgrinberg/microdot";
      flake = false;
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      micropython-lib-src,
      microdot-src
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

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
            mpremote fs rm config.py
            mpremote exec "
with open('config.py', 'w') as f:
    f.write('WIFI_NAME = \"$WIFI_NAME\"\n')
    f.write('WIFI_PASSWORD = \"$WIFI_PASSWORD\"\n')
"
                else
                    echo "WIFI_NAME or WIFI_PASSWORD not set. Skipping config generation."
                fi

            # Should also etch it for starting without running it locally. In theory. Is untested. Without warranty.
            mpremote cp -r ./src/* :.
            mpremote run ./src/main.py
        '';

        # Custom script for the compile and upload command
        dm-flash = pkgs.writeShellScriptBin "dm-flash" ''
          esptool --chip esp32c6 --baud 460800 erase-flash
          esptool --chip esp32c6 --baud 460800 write-flash -z 0x0 ESP32_GENERIC_C6-20260406-v1.28.0.bin

          install-microdot
          install-aioble
        '';

        # Fetch the stubs specifically for the ESP32
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

            mkdir -p  ./typings/aioble/
            cp ${micropython-lib-src}/micropython/bluetooth/aioble/aioble/* ./typings/aioble/
        '';

        install-microdot = pkgs.writeShellScriptBin "install-microdot" ''
            echo "Installing microdot to connected device..."

            mpremote mkdir fs :/lib
            mpremote fs mkdir :/lib/microdot
            mpremote fs cp ${microdot-src}/src/microdot/* :lib/microdot

            mkdir -p ./typings/microdot
            cp ${microdot-src}/src/microdot/* ./typings/microdot/
        '';
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            esptool
            dm-flash
            thonny
            mpremote
            run-main
            python313
            install-microdot
            install-aioble
          ];

          shellHook = ''
            echo "Esptool Dev Shell"

            echo "Exporting pythonpath with value ${esp32Stubs}/publish/micropython-v1_28_0-esp32-stubs"
            export PYTHONPATH="$PYTHONPATH:${esp32Stubs}/publish/micropython-v1_28_0-esp32-stubs"

            mkdir -p ./typings/

            ln -sf ${esp32Stubs}/publish/micropython-v1_28_0-esp32-stubs/* ./typings/

            # Generated with the power of AI (Googles Gemini)!
            # Symlink the generated .pyi stub to the current directory if it doesn't exist
            # Explicitly name types you want to control. Defaults to str | None. Picks up types from .env.default
            if [ -f .env.default ]; then
                rm "./typings/config.pyi"
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

            echo "Run 'dm-flash' to flash a connected device"
          '';
        };
      }
    );
}
