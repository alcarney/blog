Compiling LaTeX Documents with Nix
==================================

The easy way
------------

::

   $ nix-shell -p texlive.combined.full
   $ latexmk main.tex


The not-so easy way
-------------------

::

   let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      tex = (pkgs.texlive.combine {
        inherit (pkgs.texlive) scheme-basic
        arydshln fontawesome5 latexmk multirow metafont pgf;
      });
    in {

      devShells.x86_64-linux.default = pkgs.mkShell {
        packages = [ tex ];
      };

Lots of looking in ``nixpkgs/pkgs/tools/typesetting/tex/texlive/tlpdb.nix``

Using a derivation
------------------

::

   packages.x86_64-linux.default = pkgs.stdenv.mkDerivation {
     pname = "my-document";
     version = "2023.10";
     src = ./.;

     buildInputs = [ tex ];
     buildPhase = ''
       echo $(pwd)
       latexmk -pdf main.tex
     '';

     installPhase = ''
       mkdir -p $out
       cp main.pdf $out/document-name.pdf
     '';
   };


::

   kpathsea: Running mktexpk --mfmode / --bdpi 600 --mag 1+0/600 --dpi 600 tcsl1095
   mkdir: cannot create directory '././homeless-shelter': Permission denied
   mktexpk: /nix/store/7z9knc5c299c6jxfdbk38g33ga3yhp57-texlive-combined-2022-texmfdist/web2c/mktexdir /homeless-shelte>
   kpathsea: Appending font creation commands to missfont.log.

https://github.com/NixOS/nixpkgs/issues/58697

https://github.com/dnadales/nix-latex-template - nice resource!
