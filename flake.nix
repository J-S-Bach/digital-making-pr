{
  description = "Esptool environment for ESP32. This is basically the same thing as arduino-cli, but in python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    micropython-lib-src = {
      url = "github:micropython/micropython-lib";
      flake = false;
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      micropython-lib-src
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
                echo "Making config.py file crispy clean!"
                mpremote fs rm config.py
                echo "Writing config.py to device"
                mpremote exec "
with open('config.py', 'w') as f:
    f.write('WIFI_NAME = \"$WIFI_NAME\"\n')
    f.write('WIFI_PASSWORD = \"$WIFI_PASSWORD\"\n')
"
                else
                    echo "WIFI_NAME or WIFI_PASSWORD not set. Skipping config generation."
                fi
            # python runner.py
            mpremote run ./src/main.py
        '';

        # Custom script for the compile and upload command
        dm-flash = pkgs.writeShellScriptBin "dm-flash" ''
          esptool --chip esp32c6 --baud 460800 write_flash -z 0x0 ESP32_GENERIC_C6-20260406-v1.28.0.bin

          mpremote mip install aioble
        '';

        # Fetch the stubs specifically for the ESP32
        esp32Stubs = pkgs.fetchFromGitHub {
          owner = "Josverl";
          repo = "micropython-stubs";
          sparseCheckout = [ "publish/micropython-v1_28_0-esp32-stubs" ];
          rev = "0f3195c43dfbf83c8219782394dfefc003bc3f63";
          sha256 = "sha256-MQlBN6KouZpc7dlSEVHXOmNXz6iXr5bQpDkTGWPCihs=";
        };

        aioble = pkgs.stdenv.mkDerivation {
          pname = "micropython-aioble";
          version = "master";
          src = micropython-lib-src;

          installPhase = ''
            mkdir -p $out/aioble
            cp -r micropython/bluetooth/aioble/aioble/* $out/aioble/
          '';
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            esptool
            dm-flash
            thonny
            mpremote
            run-main
            aioble
            python313

          ];

          shellHook = ''
            echo "Esptool Dev Shell"

            echo "Exporting pythonpath with value ${esp32Stubs}/publish/micropython-v1_28_0-esp32-stubs"
            export PYTHONPATH="$PYTHONPATH:${esp32Stubs}/publish/micropython-v1_28_0-esp32-stubs"

            mkdir ./typings/

            ln -s ${esp32Stubs}/publish/micropython-v1_28_0-esp32-stubs/* ./typings/
            ln -sn ${aioble}/aioble ./typings/aioble

            # Generated with the power of AI (Googles Gemini)!
            # Symlink the generated .pyi stub to the current directory if it doesn't exist
            if [ -f .env ]; then
                grep -v '^#' .env | grep '=' | cut -d'=' -f1 | while read -r key; do
                key=$(echo "$key" | xargs)
                if [ "$key" = "WIFI_SSID" ]; then
                    echo "SSID: str" >> "./typings/config.pyi"
                elif [ "$key" = "WIFI_PASS" ]; then
                    echo "PASS: str" >> "./typings/config.pyi"
                else
                    echo "$key: str" >> "./typings/config.pyi"
                fi
                done
            else
                echo "No .env file found; skipping config.pyi generation."
            fi



            echo "Run 'dm-flash' to flash a connected device"
          '';
        };
      }
    );
}
