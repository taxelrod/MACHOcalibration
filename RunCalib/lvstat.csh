#!/bin/csh
setenv MPHOT /p/lscratchh/dawson29/macho_photometry
setenv MSTAR /p/lscratchh/axelrod2/MSTAR
setenv TMP /p/lscratchh/axelrod2/tmp
setenv STAT /p/lscratchh/axelrod2/lcStat

set field=$1
set CODE=..
set OUTSTAT=${STAT}/F_$field

foreach f (${OUTSTAT}/F_$field*.lcstat)
	echo $f
	${CODE}/lvExtract.py $f 1.2 0.1 > $f:r.lvstat
end
