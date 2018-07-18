#!/bin/csh

setenv TMP /p/lscratchh/axelrod2/tmp
setenv STAT /p/lscratchh/axelrod2/lcStat

set field=$1
set OUTSTAT=${STAT}/F_$field

rm -rf ${OUTSTAT}
rm -f ${TMP}/*
