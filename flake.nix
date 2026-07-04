{
  description = "Esptool environment for ESP32. This is basically the same thing as arduino-cli, but in python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        run-main = pkgs.writeShellScriptBin "run-main" ''
          echo "Executing local file main.py on ESP32"
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
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            esptool
            dm-flash
            thonny
            mpremote
            run-main
          ];

          shellHook = ''


            echo "Esptool Dev Shell"

            echo "Exporting pythonpath with value ${esp32Stubs}/publish/micropython-v1_28_0-esp32-stubs"
            export PYTHONPATH="$PYTHONPATH:${esp32Stubs}/publish/micropython-v1_28_0-esp32-stubs"

            mkdir ./.stubs/

            ln -s ${esp32Stubs}/publish/micropython-v1_28_0-esp32-stubs/* ./.stubs/


            echo "Run 'dm-flash' to flash a connected device"
          '';
        };
      }
    );
}
