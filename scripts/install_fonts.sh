#!/usr/bin/env sh

_fontdir="/usr/share/fonts/truetype"
_gfwgeturl="https://fonts.google.com/download?family="
_gfdir="$_fontdir/google-fonts"
_googlefonts="Lato Nunito Poppins Roboto Rubik"

echo "Installing Google Fonts"
for _font in $_googlefonts
do
  echo "> Checking $_font font family installation"
  if [ $(fc-list | grep -i $_font | wc -c) -eq 0 ] ; then
    echo " Dowloading and extracting font files"
    if wget -q -O $_font.zip "${_gfwgeturl}${_font}" ; then
      mkdir -p $_gfdir
      unzip -uo -d $_gfdir ./$_font.zip &> /dev/null

      echo " Installing fonts in $_gfdir and updating the font cache"
      chmod -R --reference=$_fontdir $_gfdir

      echo " Deleting the dowloaded archive"
      rm ./$_font.zip

      echo " ✔ Done"
    else
      echo " ✖ $_font could not be downloaded"
    fi
  else
    echo " ✔ $_font font family already installed"
  fi
done

echo "Updating font cache"
fc-cache -f
