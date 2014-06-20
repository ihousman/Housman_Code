import scipy
import numpy
from numpy import numarray
from numpy.numarray import nd_image
Dir = 'R:/NAFD/Landtrendr/LT_lite/test_inputs/'
image = Dir + 'ud_stack_clip.tif'
#arr = scipy.imread(image)

array = numpy.array(numpy.random.sample(20)).reshape((2,10))
kernel = numpy.array(range(1))
output = nd_image.correlate1d(array, kernel)
output = nd_image.laplace(array)
print array
print output
