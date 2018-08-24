#!/bin/csh
setenv MPHOT /p/lscratchh/dawson29/macho_photometry
setenv MSTAR /p/lscratchh/axelrod2/MSTAR
setenv TMP /p/lscratchh/axelrod2/tmp
setenv STAT /p/lscratchh/axelrod2/lcStat

set field=$1
set CODE=..
set OUTSTAT=${STAT}/F_$field
set OUTCOMBSTAT=${OUTSTAT}/F_$field.all.lcstat

rm -f $OUTCOMBSTAT
touch $OUTCOMBSTAT

foreach f (${OUTSTAT}/*[0-9].lcstat)
	cat $f >> $OUTCOMBSTAT
end
