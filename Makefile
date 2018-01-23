calib.so : calib.pyf calib_lc4.f
	f2py -c calib.pyf calib_lc4.f
