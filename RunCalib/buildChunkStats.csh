setenv MPHOT /p/lscratchh/dawson29/macho_photometry
setenv MSTAR /p/lscratchh/axelrod2/MSTAR
setenv TMP /p/lscratchh/axelrod2/tmp
setenv OUT /p/lscratchh/axelrod2/lcStat

foreach c (`cat chunklist`)
	echo '# F T S Rchunk RA DEC Rmed Rmad RmeanErr Vmed Vmad VmeanErr WScoeff WScoeffp' > ${OUT}/F_77_C$c.chunkstat
	cat ${OUT}/F_77*.lvstat | awk '$4=='"$c" >> ${OUT}/F_77_C$c.chunkstat
end
