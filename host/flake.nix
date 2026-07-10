{
  description = "Python project dev environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        recess-deps = with pkgs; [
          stdenv.cc.cc.lib
          zlib
        ];

        uv-install = pkgs.writeShellScriptBin "uv-install" ''
            uv sync
        '';
      in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python313
            uv
            uv-install
          ];

          shellHook = ''
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath recess-deps}:$LD_LIBRARY_PATH"
            uv-install
            echo "Python ecosystem initialized with 'uv'"
          '';
        };
      });
}
