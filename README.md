# kmlundup
Check *.kml file for duplicated points/tracks.

This script looks for unique points and tracks in KML file exported from SAS.Planet. 
It extracts date from 'time: YYYY-MM-DDTHH:MM:SSZ'  placed by Locus Pro into description field and move it back in the SASPlanet format 'DD.MM.YYYY HH:MM:SS'.
Scripts takes two command line arguments --points or --tracks and source filename. 
