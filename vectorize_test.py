import numpy
from scipy import stats, ndimage
import time
from r_numpy_lib import *



##def lin_regress(in_y, in_x, fun = 'stats.linregress'):
##    out_array = []
##    for y in three_to_two(in_y):
##        
##        exec('out_array.append('+fun+'(in_x, y))')
##    return two_to_three(numpy.array(out_array), in_y)
##
##

def lrgrs(in_ys, in_xs):
    #print in_ys
    #return in_ys
    return stats.linregress(in_ys, in_xs)

vfunc = numpy.vectorize(lrgrs, otypes = [numpy.ndarray])

img_in = 'R:/NAFD/Landtrendr/tSAT/test_inputs/ud_stack_clip.tif'
image = brick(img_in, dt = 'Int16')
In = three_to_two(image)
xs = numpy.arange(len(In[0]))* len(In)

t1 = time.time()
print numpy.apply_along_axis(lrgrs, 1, In, xs)
t2 = time.time()
print t2-t1
#vfunc(In, xs)
