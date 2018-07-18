#!/bin/csh

setenv MPHOT /p/lscratchh/dawson29/macho_photometry
setenv MSTAR /p/lscratchh/axelrod2/MSTAR
setenv TMP /p/lscratchh/axelrod2/tmp
setenv STAT /p/lscratchh/axelrod2/lcStat
setenv OUT /p/lscratchh/axelrod2/XMATCH

set field=$1
set CODE=..
set OUTMATCH=${OUT}/F_$field

${CODE}/fitMags.py $OUTMATCH/F_$field.all.xmatch $OUTMATCH/F_$field.photfit

