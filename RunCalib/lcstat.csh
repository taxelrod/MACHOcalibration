setenv MPHOT /p/lscratchh/dawson29/macho_photometry
setenv MSTAR /p/lscratchh/axelrod2/MSTAR
setenv TMP /p/lscratchh/axelrod2/tmp
setenv OUT /p/lscratchh/axelrod2/lcStat

foreach f (${MPHOT}/F_77/*.gz)
	echo $f
	gunzip -c $f > ${TMP}/$f:t:r
	./lcStats.py ${TMP}/$f:t:r ${OUT}/$f:t:r.lcstat ${MSTAR}/DumpStar_77.txt
	rm -f ${TMP}/$f:t:r
end
