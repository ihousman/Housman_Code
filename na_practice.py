import sys, os
tools_dir = 'O:/03_Process/Tools/'
sys.path.append(tools_dir)
from r_numpy_lib import *
#from scipy import interpolate
#import scipy
#from scipy import stats



##x = numpy.arange(100, dtype = 'float32').reshape((5,4, 5))
##
##x[(x >= 20) & ( x < 40)] = numpy.nan
##
##A = numpy.apply_along_axis(tf, 0, x)
##print A
###y = numpy.ma.masked_where(x == 5, x)
###print 'x', x
##print
##print
#z = fill_nan(y)
##ii = 0
##last = 0
##def quick_linregress(data, y_data = ''):
##    global ii, last
##    last = status_bar(ii,ll, last = last)
##    ii += 1
##    #print data
##    
##    if y_data == '':
##        y_data = range(len(data))
##    stat = stats.linregress(data, y_data)
##    return stat
##
###A = numpy.apply_along_axis(quick_linregress, 0, x)
##
ii = 0
last = 0
def tf(in_array, no_data_value):
    global ii, last
    in_array[in_array == no_data_value] = numpy.nan
    last = status_bar(ii,ll, last = last)
    not_nan = numpy.logical_not(numpy.isnan(in_array))
    indices = numpy.arange(len(in_array))
    ii += 1
    try:
        return numpy.interp(indices, indices[not_nan], in_array[not_nan])
    except:
        return in_array
def fill_stack(in_stack, out_stack, no_data_value):
    global ii, last, ll
    ti = tiled_image(out_image, in_image, outline_tiles = True)
    
    for xo,yo,w,h in ti.chunk_list:
        ii, last = 0,0
        r = brick(in_image, 'Float32', xo,yo,w,h)
        ll = r.shape[1] * r.shape[2]
        a = numpy.apply_along_axis(tf, 0, r, args = (no_data_value,))
        ti.add_tile(a, xo, yo)

        a = None
        del a
        r = None
        del r
    ti.rm()


from scipy import ndimage
import matplotlib.pyplot as plt
from sklearn.mixture import GMM

np.random.seed(1)
n = 10
l = 256
im = np.zeros((l, l))
points = l*np.random.random((2, n**2))
im[(points[0]).astype(np.int), (points[1]).astype(np.int)] = 1
im = ndimage.gaussian_filter(im, sigma=l/(4.*n))

mask = (im > im.mean()).astype(np.float)


img = mask + 0.3*np.random.randn(*mask.shape)

binary_img = img > 0.5

# Remove small white regions
open_img = ndimage.binary_opening(binary_img)
# Remove small black hole
close_img = ndimage.binary_closing(open_img)

plt.figure(figsize=(12, 3))

l = 128

plt.subplot(141)
plt.imshow(binary_img[:l, :l], cmap=plt.cm.gray)
plt.axis('off')
plt.subplot(142)
plt.imshow(open_img[:l, :l], cmap=plt.cm.gray)
plt.axis('off')
plt.subplot(143)
plt.imshow(close_img[:l, :l], cmap=plt.cm.gray)
plt.axis('off')
plt.subplot(144)
plt.imshow(mask[:l, :l], cmap=plt.cm.gray)
plt.contour(close_img[:l, :l], [0.5], linewidths=2, colors='r')
plt.axis('off')

plt.subplots_adjust(wspace=0.02, hspace=0.3, top=1, bottom=0.1, left=0, right=1)

plt.show()
##in_image = 'X:/Landsat/169069/stacks/169069_nbr_stack.img'
##out_image = in_image + '_filled.img'
##ndv = -9999
##fill_stack(in_image, out_image, ndv)


##i = brick(in_image, dt = 'Float32')
##i[i == -9999] = numpy.nan
##ll = i.shape[1] * i.shape[2]
##
##t1 = time.time()
##
##A = numpy.apply_along_axis(tf, 0, i)
##stack(A, in_image + '_filled.img', in_image,array_list = True)
##t2 = time.time()
##print t2 - t1

i = None
A = None
