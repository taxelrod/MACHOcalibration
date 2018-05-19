#!/bin/csh

setenv MPHOT /p/lscratchh/dawson29/macho_photometry
setenv MSTAR /p/lscratchh/axelrod2/MSTAR
setenv TMP /p/lscratchh/axelrod2/tmp
setenv STAT /p/lscratchh/axelrod2/lcStat
setenv OUT /p/lscratchh/axelrod2/XMATCH

set field=$1

set OUTSTAT=${STAT}/F_$field

foreach f (${OUTSTAT}/F_${field}_C*.chunkstat)
	stilts tskymatch2 ifmt1=ascii omode=out ofmt=ascii error=1.5 out=${OUT}/$f:t:r.xmatch $f /p/lscratchh/axelrod2/SMASH_LMC/LMCbody_stars_unique_$field.fits
end
