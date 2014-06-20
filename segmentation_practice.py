#from __future__ import print_function
from r_numpy_lib import *
import matplotlib.pyplot as plt
import numpy as np

from skimage.data import lena
from skimage.segmentation import felzenszwalb, slic, quickshift
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
from scipy import misc
#img = img_as_float(lena()[::2, ::2])
img_name = 'B:/2_SatelliteImagery/Gmaps/Imagery/Test4/reprojected_1m/tile_91.4761820742629_22.5230230586932_17_j_clip_proj.img'
img = brick(img_name,'',50,50,150,150)
#img = scipy.misc.imread(img_name)
print len(img)
print img
img = numpy.transpose(img, axes = [1,2,0])
print img
print 'Computing Felzenszwalkbs segmentation'
segments_fz = felzenszwalb(img, scale=20, sigma=1, min_size=50)
print 'Computing slic k-means segmentation'
segments_slic = slic(img, compactness=10, n_segments=50, sigma=1, max_iter = 50)
print 'Computing quickshift segmentation'
segments_quick = quickshift(img, kernel_size=5, max_dist=50, sigma = 1,ratio=1)

##print "Felzenszwalb's number of segments: %d" % len(np.unique(segments_fz))
##print "Slic number of segments: %d" % len(np.unique(segments_slic))
##print "Quickshift number of segments: %d" % len(np.unique(segments_quick))

fig, ax = plt.subplots(1, 3)
fig.set_size_inches(8, 3, forward=True)
plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.05, 0.05)

ax[0].imshow(mark_boundaries(img, segments_fz))
ax[0].set_title("Felzenszwalbs's method")
ax[1].imshow(mark_boundaries(img, segments_slic))
ax[1].set_title("SLIC")
ax[2].imshow(mark_boundaries(img, segments_quick))
ax[2].set_title("Quickshift")
for a in ax:
    a.set_xticks(())
    a.set_yticks(())
plt.show()


##b = os.path.splitext(img_name)[0]
##out_fz = b + '_fz.jpg'
##out_slic = b + 'slic.jpg'
##out_quick = b + 'quickshift2.jpg'
##scipy.misc.imsave(out_fz,mark_boundaries(img, segments_fz))
##scipy.misc.imsave(out_slic,mark_boundaries(img,segments_slic))
##scipy.misc.imsave(out_quick,mark_boundaries(img,segments_quick))

##import numpy as np
##from scipy import ndimage as nd
##import matplotlib.pyplot as plt
##
##from skimage.filter import sobel
##from skimage.segmentation import slic, join_segmentations
##from skimage.morphology import watershed
##from skimage.color import label2rgb
##from skimage import data, img_as_float
##
##coins = img_as_float(data.coins())
##
### make segmentation using edge-detection and watershed
##edges = sobel(coins)
##markers = np.zeros_like(coins)
##foreground, background = 1, 2
##markers[coins < 30.0 / 255] = background
##markers[coins > 150.0 / 255] = foreground
##
##ws = watershed(edges, markers)
##seg1 = nd.label(ws == foreground)[0]
##
### make segmentation using SLIC superpixels
##seg2 = slic(coins, n_segments=117, max_iter=5, sigma=1, compactness=0.5,
##            multichannel=False)
##
### combine the two
##segj = join_segmentations(seg1, seg2)
##
### show the segmentations
##fig, axes = plt.subplots(ncols=4, figsize=(9, 2.5))
##axes[0].imshow(coins, cmap=plt.cm.gray, interpolation='nearest')
##axes[0].set_title('Image')
##
##color1 = label2rgb(seg1, image=coins, bg_label=0)
##axes[1].imshow(color1, interpolation='nearest')
##axes[1].set_title('Sobel+Watershed')
##
##color2 = label2rgb(seg2, image=coins, image_alpha=0.5)
##axes[2].imshow(color2, interpolation='nearest')
##axes[2].set_title('SLIC superpixels')
##
##color3 = label2rgb(segj, image=coins, image_alpha=0.5)
##axes[3].imshow(color3, interpolation='nearest')
##axes[3].set_title('Join')
##
##for ax in axes:
##    ax.axis('off')
##plt.subplots_adjust(hspace=0.01, wspace=0.01, top=1, bottom=0, left=0, right=1)
##plt.show()