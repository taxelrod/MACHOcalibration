c$$$c	read directly from clc/sodset ascii output
c$$$c
c$$$c	simpler than calib_ceph2
c$$$c	does not require independent color/phase file
c$$$c	good for Cepheids with the majority of photometry
c$$$c	in both B and R, ie. not in dead amp region.
c$$$
c$$$	program calib_cephlc
c$$$
c$$$      	character *50 file1,file2,file3
c$$$      	parameter (m=5000)
c$$$      	real ar(m),aer(m),ab(m),aeb(m),asee(m),asky(m)
c$$$    	integer arf1(m),abf1(m),arf3(m),abf3(m)
c$$$	real at(m),aair(m)
c$$$	character *5 ps(m),temp
c$$$	integer psflag(m),l,max1,max2
c$$$	real junkday,col(m)
c$$$	double precision phase(m)
c$$$	integer field,til,seq,chunk
c$$$      	real xt,co,a0,a1,b0,b1,bje,bjw,bjo
c$$$      	real a3,a4,b3,b4
c$$$	real dbjit
c$$$	real omb,omr,omc,ov,or
c$$$	real junkb
c$$$	real period
c$$$
c$$$	character *5 jc
c$$$	character *20 je
c$$$	character *1 jd
c$$$	character *6 jf
c$$$	integer rtobs,btobs
c$$$	real r,er,b,eb,see,sky,rx,ry,bx,by
c$$$	real jr,t,air
c$$$	integer rf1,rf2,rf3,bf1,bf2,bf3
c$$$	integer s,ji,obs,exp,ramp,bamp
c$$$	integer bsky
c$$$	real bsee
c$$$
c$$$	character *7 head1
c$$$	character *16 starid
c$$$	character *20 head3
c$$$	character *40 starpos
c$$$	character *60 head2
c$$$	
c$$$      
c$$$c	--------------------------------------------------
c$$$c	input data
c$$$c	--------------------------------------------------
c$$$
c$$$      	write (*,*)
c$$$      	write (*,*) 'input file ' 
c$$$      	read (*,'(A50)')  file1
c$$$      	write (*,*) 'output file ' 
c$$$      	read (*,'(A50)')  file3
c$$$      	write (*,*)
c$$$
c$$$c	--------------------------------------------------
c$$$c	read "lc" file (clc/sodset ascii output)
c$$$c	collect interesting (according to Alves) data
c$$$c	require simultaneous red and blue photometry
c$$$c	--------------------------------------------------
c$$$
c$$$c	format (F12.4,4F8.3,F9.3,F10.3,2I7,A11)
c$$$50	format (F12.4,4F8.3,F9.3,F10.3,2I7,A11,4F9.2)
c$$$
c$$$
c$$$      	open (unit=1,file=file1)
c$$$	read (1,'(A7,A16,A20,A40)') head1,starid,head3,starpos
c$$$	read (1,*)
c$$$	read (1,*)
c$$$	read (1,*)
c$$$	read (1,*)
c$$$	read (1,*)
c$$$	read (1,'(A60,I8)') head2,chunk
c$$$	read (1,*)
c$$$	read (1,*)
c$$$	read (1,*)
c$$$
c$$$	open (unit=9,file='foobar')
c$$$	s = index(starid,'.') - 1
c$$$	write (9,*) starid(:s)
c$$$	rewind (9)
c$$$	read (9,*) field
c$$$	close (unit=9)
c$$$
c$$$	j = 0
c$$$      	do 100 k=1,m
c$$$
c$$$
c$$$c          read (1,*,END=110) t,jc,ji,ji,jf,air,exp,
c$$$c     &		r,er,ramp,rf1,rf2,rf3,rx,ry,rtobs,see,sky,
c$$$c     &		b,eb,bamp,bf1,bf2,bf3,bx,by
c$$$
c$$$          read (1,*,END=110) t,ji,jc,exp,ji,jf,air, 
c$$$     &		r,er,ji,rf1,ji,ji,ji,ji,ramp,rx,ry,sky,see,rtobs,rf3,
c$$$     &		b,eb,ji,bf1,ji,ji,ji,ji,bamp,bx,by,bsky,bsee,btobs,bf3
c$$$
c$$$
c$$$	  if (r.ge.(-15).and.b.ge.(-15)) then
c$$$	  if (r.lt.(-2).and.b.lt.(-2)) then
c$$$	  if (er.gt.0.and.er.le.(1.0)) then
c$$$	  if (eb.gt.0.and.eb.le.(1.0)) then
c$$$
c$$$	     	j = j + 1
c$$$		at(j) = t
c$$$		ar(j) = r 
c$$$		aer(j) = er
c$$$		ab(j) = b
c$$$		aeb(j) = eb
c$$$		asee(j) = see
c$$$		aair(j) = air
c$$$		arf1(j) = rf1
c$$$		abf1(j) = bf1
c$$$		ps(j) = jc
c$$$		arf3(j) = rf3
c$$$		abf3(j) = bf3
c$$$
c$$$	 	if (ps(j).eq.'East ') then
c$$$	   	  psflag(j) = 0
c$$$	 	else
c$$$	   	  psflag(j) = 1
c$$$	 	endif
c$$$
c$$$c	 	phase(j) = mod(at(j),period)/period
c$$$	 	col(j) = ab(j) - ar(j)
c$$$	 	max1 = j
c$$$
c$$$
c$$$	  endif
c$$$	  endif
c$$$	  endif
c$$$	  endif
c$$$	
c$$$
c$$$100   	continue
c$$$110   	continue
c$$$	close(unit=1)
c$$$
c$$$
c$$$c	--------------------------------------------------
c$$$c	get blujitter and calibrations data
c$$$c	--------------------------------------------------
c$$$
c$$$	call get_zps98(field,chunk,xt,a0,a1,b0,b1,ierr)
c$$$	call get_bj(field,chunk,bje,bjw,bjo)
c$$$	call get_co(field,chunk,co)
c$$$
c$$$	a3 = a0 + co
c$$$        a4 = a1 + 0.022*xt
c$$$	b3 = b0 + co
c$$$      	b4 = b1 + 0.004*xt
c$$$	
c$$$	write (*,*) a0,a1,b0,b1,co
c$$$	write (*,*) bje,bjw,bjo
c$$$	write (*,*) a3,a4,b3,b4
c$$$
c$$$c	--------------------------------------------------
c$$$c	write out "rv" file
c$$$c	--------------------------------------------------
c$$$	
c$$$      	open (unit=3,file=file3)
c$$$
c$$$c500    format (F10.4,4F7.3,F9.3,F10.3,2I6,1x,A5,I1,F14.8,F7.3,3(F8.3))
c$$$c500   	format (F10.4,F12.8,2(F7.3,F6.3),2F8.3,F7.3,2I6,2F6.2,,1x,A5)
c$$$500    	format (F10.4,2(F7.3,F6.3),3F8.3,2I7,2x,F6.2,2x,F6.2,2x,A5,2I3)
c$$$
c$$$	write (3,'(A3,A16,I4,5x,A40)') '#  ',starid,chunk,starpos
c$$$
c$$$	do 1000 i=1,max1
c$$$
c$$$	omb = 0.0
c$$$	dbjit = 0.0
c$$$
c$$$	if (psflag(i).eq.0) then
c$$$	   dbjit = bje*( col(i) - bjo )
c$$$	else
c$$$	   dbjit = bjw*( col(i) - bjo )
c$$$	endif
c$$$
c$$$	omb = ab(i) + dbjit
c$$$	omr = ar(i)
c$$$	omc = omb - omr
c$$$	ov = a3 + a4*omc + omb
c$$$	or = b3 + b4*omc + omr
c$$$	  
c$$$          write (3,500) at(i),or,aer(i),ov,aeb(i),
c$$$     &	    ar(i),ab(i),dbjit,abf1(i),arf1(i),asee(i),aair(i),ps(i),
c$$$     &		abf3(i),arf3(i)
c$$$
c$$$1000	continue
c$$$
c$$$      	end



c	********************************************************

c	--------------------------------------------------------
c	enter fld, chunk and get back bj coefficients
c	call get_bj(fld,ck,bje1,bjw1,bjo)
c	--------------------------------------------------------

	subroutine get_bj(fld,ck,bj_e1,bj_w1,bj_colo)

	real bj_e1,bj_w1,bj_colo
	integer fld,ck,n
	parameter (m=128)
	real b(m),mc(m),tbj
	integer c(m)
	character *30 name
	character *3 cfld

c	--------------------------------------------------------
c	open bj.data and get "west" coefficient for chunk
c	--------------------------------------------------------

	name = 'CO/bj.data'
	open (unit=9,file=name,status='OLD')
	
	do 100 i=1,m
	  read (9,*,END=110) c(i),b(i)
100	continue
110	continue

	close(9)

	do 200 i=1,m
	if (c(i).eq.ck) then
	  tbj = b(i)
	endif
200	continue

c	------------------------------
c	interpret style of template
c	style(e) = 0, style(w) = 1
c	------------------------------

	style = 0
	if (fld.eq.5) then
	  style = 1
	endif
	if (fld.eq.9) then
	  style = 1
	endif
	if (fld.eq.14) then
	  style = 1
	endif
	if (fld.eq.15) then
	  style = 1
	endif

c	------------------------------
c	east of pier style
c	style = 0
c	------------------------------

	if (style.eq.0) then
	  if (ck.ge.24.and.ck.le.39) then
		bj_e1 = -1*tbj
		bj_w1 = 0
          else
		bj_e1 = 0
		bj_w1 = tbj
          endif
	endif

c	------------------------------
c	west of pier style
c	style = 1
c	------------------------------

	if (style.eq.1) then
	  if (ck.le.7.or.ck.ge.120) then
		bj_e1 = 0
		bj_w1 = tbj
	  else
		bj_e1 = -1*tbj
		bj_w1 = 0
	  endif
	endif

c	--------------------------------------------------------
c	open psf_mcol file (by field) and get mcol for chunk
c	--------------------------------------------------------

	open (unit=9,file='foobar',status='OLD')
	write (9,'(I3.3)') fld
	rewind(9)
	read (9,'(A3)') cfld
	close(9)

	name = 'CO/psf_mcol.'//cfld
	open (unit=9,file=name,status='OLD')

	do 500 i=1,m
		read (9,*,END=510) n,c(i),mc(i),n
500	continue
510	continue

	do 600 i=1,m
	if (c(i).eq.ck) then
          if (mc(i).le.(0.35)) then
                bj_colo = -0.05
          else
                bj_colo = -0.4 + mc(i)
          endif
	endif
600	continue

	end

c	********************************************************

c	--------------------------------------------------------
c	enter fld, chunk  and get back co
c	call get_co(fld,ck,co)
c	--------------------------------------------------------

	subroutine get_co(fld,ck,rco)

	real rco
	integer fld,ck
	parameter (m=128)
	real b,r(m)
	integer c(m)
	character *30 name
	character *3 cfld

	open (unit=9,file='foobar')
	write (9,'(I3.3)') fld
	rewind(9)
	read (9,'(A3)') cfld
	close(9)

	name = 'CO/tmpl_co.'//cfld
	open (unit=9,file=name,status='OLD')

	do 100 i=1,m
	  read (9,*,END=110) c(i),b,r(i)
100	continue
110	continue

	do 200 i=1,m
      
	if (c(i).eq.ck) then
	  rco = r(i)
	endif

200	continue

	end


c	********************************************************

c       --------------------------------------------------------
c       enter fld and chunk and get back calib coeffs
c       call get_zps(fld,ck,xt,a0,a1,b0,b1)
c
c       fields may be in any order, counts on one blank line
c       separating 4 lines of data per field
c       --------------------------------------------------------

        subroutine get_zps98(fld,ck,exp,xt,a0,a1,b0,b1,ierr)

	integer q,r
        parameter (q=500)
        parameter (r=4)
        integer max1,max2
        integer fld,ck,ierr
	real exp
        real xt,a0,a1,b0,b1
        real a0_03(q),a1_03(q),b0_03(q),b1_03(q)
        real a0_19(q),a1_19(q),b0_19(q),b1_19(q)
        real da19,db19
        real a0_51(q),a1_51(q),b0_51(q),b1_51(q)
        real da51,db51
        real a0_31(q),a1_31(q),b0_31(q),b1_31(q)
        real da31,db31
        integer mfld(q),obs
        real mair(q,r)
	integer gotfld


c       --------------------------------------------------------
c       open and read "tmpl_data98" file
c       --------------------------------------------------------

        open (unit=19, file='CO/tmpl_data98',status='OLD')
        read (19,*)
        read (19,*)
        read (19,*)
        read (19,*)
        read (19,*)
        read (19,*)
        read (19,*)
        read (19,*)

        do 50 i=1,q
        read (19,*,END=60) mfld(i),obs,
     &	mair(i,1),a0_03(i),a1_03(i),b0_03(i),b1_03(i)
        read (19,*,END=60) obs,mair(i,2),da19,a1_19(i),db19,b1_19(i)
        read (19,*,END=60) obs,mair(i,3),da51,a1_51(i),db51,b1_51(i)
        read (19,*,END=60) obs,mair(i,4),da31,a1_31(i),db31,b1_31(i)
        read (19,*,END=60) 

        a0_19(i) = a0_03(i) + da19 
        b0_19(i) = b0_03(i) + db19 
        a0_51(i) = a0_03(i) + da51
        b0_51(i) = b0_03(i) + db51
        a0_31(i) = a0_03(i) + da31
        b0_31(i) = b0_03(i) + db31
        max1 = i
50      continue
60      continue
        close (unit=19) 

c       --------------------------------------------------------
c       find correct coefficient
c       --------------------------------------------------------

	gotfld = 0
	ierr = 0
        do 2000 i=1,max1
        if (fld.eq.mfld(i)) then
	  gotfld = 1
          if (ck.ge.0.and.ck.le.7) then
                xt = mair(i,1)
                a0 = a0_03(i)
                a1 = a1_03(i)
                b0 = b0_03(i)
                b1 = b1_03(i)
          endif
          if (ck.ge.120.and.ck.le.127) then
                xt = mair(i,1)
                a0 = a0_03(i)
                a1 = a1_03(i)
                b0 = b0_03(i)
                b1 = b1_03(i)
          endif
          if (ck.ge.8.and.ck.le.23) then
                xt = mair(i,2)
                a0 = a0_19(i)
                a1 = a1_19(i)
                b0 = b0_19(i)
                b1 = b1_19(i)
          endif
          if (ck.ge.40.and.ck.le.55) then
                xt = mair(i,3)
                a0 = a0_51(i)
                a1 = a1_51(i)
                b0 = b0_51(i)
                b1 = b1_51(i)
          endif
          if (ck.ge.24.and.ck.le.39) then
                xt = mair(i,4)
                a0 = a0_31(i)
                a1 = a1_31(i)
                b0 = b0_31(i)
                b1 = b1_31(i)
          endif
        endif
2000    continue
	
	if (gotfld.eq.0) then
                xt = 1.3
                a0 = 18.06 + 2.5*alog10(exp)
                a1 = a1_31(1)
                b0 = 17.807 + 2.5*alog10(exp)
                b1 = b1_31(1)
		ierr = 1
	endif


        end





