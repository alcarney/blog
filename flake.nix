{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-22.05";
  };

  outputs = { self, nixpkgs }:

    let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
    in {
    devShells.x86_64-linux.default = pkgs.mkShell {
      packages = [
        pkgs.ablog
        pkgs.nodejs
        pkgs.nodePackages.tailwindcss
        pkgs.nodePackages."@tailwindcss/typography"
      ];
    };
  };
}
