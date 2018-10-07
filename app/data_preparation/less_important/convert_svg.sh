#!/bin/bash
for var in "$@"
do
	s=${var##*/}
	base=${s%.svg}
	echo 'converting' $var
	inkscape -f $var -e $base.png
	echo 'done!'
	echo '*****'
done
