{
  description = "Epitech headers fixer";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python311
          ];
        };

        formatter = pkgs.nixpkgs-fmt;

        packages = {
          EpiHeader =
            let
              pypkgs = pkgs.python311Packages;
            in
            pypkgs.buildPythonPackage {
              pname = "EpiHeader";
              version = "0.0.1";
              src = ./.;

              nativeBuildInputs = with pkgs; [
                makeWrapper
              ];
            };

          default = self.packages.${system}.EpiHeader;
        };
      });
}
