#!/bin/bash

filename=$1

if [ -f "$filename" ]; then
  #remove windows carriage return symbols
  sed -i 's/\r//g' "$filename"
  # <kml xmlns="http://earth.google.com/kml/2.2"> we should remove xmlns="http://earth.google.com/kml/2.2" in preventing if statements error.
  sed -i 's|<kml xmlns="http://earth.google.com/kml/2.2">|<kml>|g' "$filename"
  ./kmlundup.py --points "$filename" > Points.kml
  ./kmlundup.py --tracks "$filename" > Tracks.kml
else
  echo "File not specified or doesn't exists" >&2
fi
