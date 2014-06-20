from r_numpy_lib import *
import os, sys, time
import matplotlib.pyplot as plt
t1 = time.time()
Dir = 'O:/02_Inputs/MODIS/Atlanta/Inputs/Spectral/'
image = Dir + 'MYD09Q1.A2006041.h11v05_h10v05.005.2008079172812_1_t.img'
info = raster_info(image)
##r('library(raster)')
##r('rast = as.matrix(raster("' + image + '"))')
##
##x = numpy.array(r['rast'])#.reshape((info['width'], info['height']))
#reproject(image, image + '_reproj_test.img', crs = info['proj4'])
array = raster(image)
#img = gdal.Open(image)
#rray = numpy.load(image)
print array
array = None
img = None
#r('gimg = readGDAL("'+ image + '")')
#print r['gimg']
#write_raster(x, image + 'test.img', image)
##print os.path.exists(image)
##
##array = plt.imread(image, format = )
##print array
