import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import scipy.stats as st


sim = st.gamma(1,loc=0,scale=.8) # Simulated
obs = st.gamma(2,loc=0,scale=0.7) # Observed
x = np.linspace(0,4,1000)
simpdf = sim.pdf(x)
obspdf = obs.pdf(x)
##plt.plot(x,simpdf,label='Simulated')
##plt.plot(x,obspdf,'r--',label='Observed')
##plt.title('PDF of Observed and Simulated Precipitation')
##plt.legend(loc='best')
##plt.show()

plt.figure(1)
simcdf = sim.cdf(x)
obscdf = obs.cdf(x)
plt.plot(x,simcdf,label='Simulated')
plt.plot(x,obscdf,'r--',label='Observed')
plt.title('CDF of Observed and Simulated Precipitation')
plt.legend(loc='best')
plt.show()

# Inverse CDF
##invcdf = interp1d(obscdf,x, bounds_error = False)
##transfer_func = invcdf(simcdf)
##
##plt.figure(2)
##plt.plot(transfer_func,x,'g-')
##plt.show()


##import sys, os
##tools_dir = 'O:/03_Process/Tools/'
##sys.path.append(tools_dir)
##from r_numpy_lib import *
##
##
##wd = 'X:/Regression_Calibration/'
##ref_image = wd +'169068_ndvi_stack_1990_2010_stats.linregress_slope_clip_intersection.img'
##corr_image = wd +'169069_ndvi_stack_1990_2009_stats.linregress_slope_clip_intersection.img'
##out = wd + 'test_hist_match2.img'
##bins = 500
##ri = raster(ref_image)
##ri = ri[ri != -9999]
##hri = numpy.histogram(ri, bins = bins)
##
##ri  = None
##
##ci = raster(corr_image)
##ci = ci[ci != -9999]
##hci = numpy.histogram(ci, bins = bins)
##
##table = [hri[1], hci[1]]
##print table
##
##ci = None
