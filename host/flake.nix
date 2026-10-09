{
  description = "Python project dev environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
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
        pkgs = nixpkgs.legacyPackages.${system};

        recess-deps = with pkgs; [
          stdenv.cc.cc.lib
          zlib
        ];

        uv-install = pkgs.writeShellScriptBin "uv-install" ''
          uv sync
        '';

        uv-run = pkgs.writeShellScriptBin "uv-run" ''
          uv run -m src.main "$@"
        '';

        run-calibration = pkgs.writeShellScriptBin "run-calibration" ''
          uv run python -m calibration.calibration_sequence
        '';

        run-ekf-tests = pkgs.writeShellScriptBin "run-ekf-tests" ''
          uv run python -m testing.ekf_testing
        '';
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python313
            uv
            uv-install
            uv-run
            run-calibration
            run-ekf-tests
          ];

          shellHook = ''
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath recess-deps}:$LD_LIBRARY_PATH"
            uv-install
            echo "Python ecosystem initialized with 'uv'."
            echo "--gui for a website hosted on http://localhost:1234"
            echo "--no-calibration for skipping calibration sequence. Calibration is needed to calibrate relative positions of multiple ESP32s"
          '';
        };
      }
    );
}
