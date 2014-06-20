from r_numpy_lib import *
from scipy import stats

in_image = 'R:/NAFD/Landtrendr/tSAT/tSTAT/Test_Data/Michigan_Forest_Z_Clip.tif'
t_out = 'R:/NAFD/Landtrendr/tSAT/tSTAT/Test_Data/slope_test_reverse2.img'
b = brick(in_image, dt = 'Float32')
start_year = 1984
years = ''#numpy.arange(start_year, start_year + len(b))
print years
#y = b[:,1,1]
###linregress_practice(y)
t1 = time.time()
out_slope = numpy.apply_along_axis(linregress_practice, 0, b, years)
##
if len(numpy.shape(out_slope)) == 2:
    out_slope = [out_slope]
stack(out_slope, t_out, in_image, dt = 'Float32', array_list = True)
brick_info(t_out, True)
t2 = time.time()
print t2 - t1
b = None
out_slope = None