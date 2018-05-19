#!/bin/csh
setenv MPHOT /p/lscratchh/dawson29/macho_photometry
setenv MSTAR /p/lscratchh/axelrod2/MSTAR
setenv TMP /p/lscratchh/axelrod2/tmp
setenv STAT /p/lscratchh/axelrod2/lcStat

set field=$1

set OUTSTAT=${STAT}/F_$field

foreach c (`cat chunklist`)
	echo '# F T S Rchunk RA DEC Rmed Rmad RmeanErr Vmed Vmad VmeanErr WScoeff WScoeffp' > ${OUTSTAT}/F_${field}_C$c.chunkstat
	cat ${OUTSTAT}/F_$field*.lvstat | awk '$4=='"$c" >> ${OUTSTAT}/F_${field}_C$c.chunkstat
end
