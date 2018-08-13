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
set OUTSTATALL=$OUTSTAT/F_$field.all.lcstat
set OUTUNBLENDED=$OUTMATCH/F_$field.unblended.xmatch
set OUTUNBLENDEDTMP=$OUTUNBLENDED.tmp
rm -f $OUTUNBLENDED
rm -f $OUTUNBLENDEDTMP

touch $OUTUNBLENDEDTMP

stilts tmatch2 matcher=sky find=all ifmt1=ascii values1="RA_1 DEC_1" ifmt2=ascii values2="RA DEC" omode=out ofmt=ascii ocmd='select NULL_GroupSize' params="3" out=${OUTUNBLENDEDTMP} ${OUTMATCHALL} ${OUTSTATALL}

sed 's/""/0.0/' $OUTUNBLENDEDTMP > $OUTUNBLENDED
