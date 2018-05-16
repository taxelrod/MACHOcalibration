setenv MPHOT /p/lscratchh/dawson29/macho_photometry
setenv MSTAR /p/lscratchh/axelrod2/MSTAR
setenv TMP /p/lscratchh/axelrod2/tmp
setenv STAT /p/lscratchh/axelrod2/lcStat
setenv OUT /p/lscratchh/axelrod2/XMATCH

foreach f (${STAT}/F_77_C*.chunkstat)
	stilts tskymatch2 ifmt1=ascii omode=out ofmt=ascii error=1.5 out=${OUT}/$f:t:r.xmatch $f /p/lscratchh/axelrod2/SMASH_LMC/LMCbody_stars_unique_77.fits
end
