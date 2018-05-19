setenv MPHOT /p/lscratchh/dawson29/macho_photometry
setenv MSTAR /p/lscratchh/axelrod2/MSTAR
setenv TMP /p/lscratchh/axelrod2/tmp
setenv OUT /p/lscratchh/axelrod2/lcStat

foreach f (${OUT}/F_77*.lcstat)
	echo $f
	./lvExtract.py $f 1.2 0.1 > $f:r.lvstat
end
