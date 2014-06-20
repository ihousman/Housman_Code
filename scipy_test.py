import scipy, os
from scipy import misc
from r_numpy_lib import *
import numpy as np
import matplotlib.pyplot as plt
from numpy import numarray
from numpy.numarray import nd_image
##l = scipy.lena()
##lena = raster('lena.png')
##print lena
##l.tofile('lena.raw')
##lena_from_raw = np.fromfile('lena.raw', dtype = np.int64)
##
##print lena_from_raw.shape
##from glob import glob
##filelist = glob('*.png')
##filelist.sort()
##
##l = scipy.lena()

##plt.imshow(l, cmap = plt.cm.gray)
##plt.contour(l, [60, 211])


image = 'O:/02_Inputs/Aster/Baltimore/Outputs/19_nlcd_sample__AST__summer__day__VCT_summer/19_nlcd_sample__AST__summer__day__VCT_summer_cubist_output.img'
#image = 'O:/02_Inputs/Aster/Baltimore/Inputs/Terrain/Baltimore_Aster_DEM.img'
l = raster(image)
info = raster_info(image)
std = info['std']
#mean = info['mean']
#mean = 150
mean = 50
stretch = 1 * 30
#plt.figure(figsize = (20, 8))
print mean, std
#plt.subplot(131)
#plt.imshow(l, cmap = plt.cm.gray)
#plt.subplot(13)
#color = plt.cm.RdBu_r




#l = focal_filter(image, fun = 'var')[0]
#l = nd_image.uniform_filter(l, size = 11)
#l = nd_image.gaussian_filter(l, sigma = 3)
##blurred_l = nd_image.gaussian_filter(l, 2)
##filtered_blurred_l = nd_image.gaussian_filter(blurred_l, 1)
##alpha = 30
##sharpened = blurred_l + alpha * (blurred_l - filtered_blurred_l)
##
##im = nd_image.gaussian_filter(l, 8)
##sx = nd_image.sobel(im, axis = 0, mode = 'constant')
##sy = nd_image.sobel(im, axis = 1, mode = 'constant')
##sob = np.hypot(sx, sy)
##
##
##
###nd_image.binary_erosion(
##plt.title('Original')
##plt.imshow(l, cmap = color, vmin = mean - stretch, vmax = mean + stretch)
##plt.subplot(132)
##plt.imshow(sharpened, cmap = color, vmin = mean - stretch, vmax = mean + stretch)
##plt.subplot(133)
##plt.imshow(blurred_l, cmap = color, vmin = mean - stretch, vmax = mean + stretch)
###plt.subplot(134)
##plt.imshow(sob, cmap = color, vmin = mean - stretch, vmax = mean + stretch)
##plt.subplots_adjust(wspace = 0, hspace = 0, top = 0.99, bottom = 0.01, left = 0.05, right = 0.99)
##plt.show()
##threshold = 50
##mask = l > threshold
#them = 
##label_im, nb_labels = nd_image.label(mask)
###write_raster(mask, os.path.splitext(image)[0] + '_them.img', image, dt = 'Int16')
##fig = plt.figure(figsize = (30,10))
##plt.subplot(131)
##plt.imshow(l)
##plt.subplot(132)
##plt.imshow(mask, cmap = plt.cm.gray)
##plt.subplot(133)
##plt.imshow(label_im, cmap = plt.cm.spectral)
##plt.subplots_adjust(wspace = 0, hspace = 0, top = 0.99, bottom = 0.01, left = 0.05, right = 0.99)
###plt.show()
##plt.savefig('fig.png')
##fig.savefig(image + 'test_plot.png', format = 'png',dpi = fig.dpi)

def map_maker(input_list, output, title = '', labels = True, colorbar = True):
    plt
    for Input in input_list:
        info = raster_info(Input)
        array = raster(Input, dt = info['dt'], band_no = band_no)
        array = raster(Input, dt = 
    
    
def clump(Input, Output, band_no = 1):
    info = raster_info(Input)
    array = raster(Input, dt = info['dt'], band_no = band_no)
    label_im, nb_labels = nd_image.label(array)
    print nb_labels
    #write_raster(label_im, Output, Input)
    array = None
    label_im = None
def clump_and_elim(Input, Output, size = 8, band_no = 1):
    info = raster_info(Input)
    array = raster(Input, dt = info['dt'], band_no = band_no)
    label_im, nb_labels = nd_image.label(array)
    sizes = nd_image.sum(array, label_im, range(nb_labels + 1))
    
    mask_size = sizes < size
    remove_pixel = mask_size[label_im]
    label_im[remove_pixel] = 0
    labels = np.unique(label_im)
    labels_clean = np.searchsorted(labels, label_im)
    write_raster(labels_clean, Output, Input)
##    #write_raster(mask_size, Output, Input)
##    fig = plt.figure(figsize = (30, 10))
##    plt.subplot(131)
##    plt.imshow(sizes, cmap = plt.cm.spectral)
##    plt.subplots_adjust(wspace = 0, hspace = 0, top = 0.99, bottom = 0.01, left = 0.05, right = 0.99)
##    #plt.show()
##    #plt.savefig('fig.png')
##    #fig.savefig(image + 'test_plot.png', format = 'png',dpi = fig.dpi)
##    array = None
    
them_image = 'O:/02_Inputs/Aster/Baltimore/Inputs/NLCD/Baltimore_Aster_NLCD_lc.img'
clump_image = os.path.splitext(them_image)[0] + '_clump.img'
clump(them_image, clump_image)
#elim_image = os.path.splitext(image)[0] + '_elim.img'
#clump_and_elim(them_image, elim_image)




