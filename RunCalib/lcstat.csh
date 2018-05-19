setenv MPHOT /p/lscratchh/dawson29/macho_photometry
setenv MSTAR /p/lscratchh/axelrod2/MSTAR
setenv TMP /p/lscratchh/axelrod2/tmp
setenv STAT /p/lscratchh/axelrod2/lcStat

field = $1

foreach f (${MPHOT}/F_$field/*.gz)
	echo $f
	echo gunzip -c $f > ${TMP}/$f:t:r
	echo ./lcStats.py ${TMP}/$f:t:r ${STAT}/$f:t:r.lcstat ${MSTAR}/DumpStar_$field.txt
	echo rm -f ${TMP}/$f:t:r
end
