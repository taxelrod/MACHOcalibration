#!/bin/csh

setenv MPHOT /p/lscratchh/dawson29/macho_photometry
setenv MSTAR /p/lscratchh/axelrod2/MSTAR
setenv TMP /p/lscratchh/axelrod2/tmp
setenv STAT /p/lscratchh/axelrod2/lcStat
setenv OUT /p/lscratchh/axelrod2/XMATCH

set field=$1

set OUTSTAT=${STAT}/F_$field
set OUTMATCH=${OUT}/F_$field

if (! -d $OUTMATCH) then
    mkdir $OUTMATCH
endif

set OUTMATCHALL=$OUTMATCH/F_$field.all.xmatch
set OUTMATCHALLTMP=$OUTMATCHALL.tmp
rm -f $OUTMATCHALL
rm -f $OUTMATCHALLTMP

touch $OUTMATCHALLTMP

foreach f (${OUTSTAT}/F_${field}_C*.chunkstat)
	stilts tskymatch2 ifmt1=ascii omode=out ofmt=ascii error=1.5 out=${OUTMATCH}/$f:t:r.xmatch $f /p/lscratchh/axelrod2/SMASH_LMC/LMCbody_stars_unique_$field.fits
	cat ${OUTMATCH}/$f:t:r.xmatch >> $OUTMATCHALLTMP
end

sed 's/""/0.0/' $OUTMATCHALLTMP > $OUTMATCHALL
