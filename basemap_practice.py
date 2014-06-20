from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from r_numpy_lib import *
image = 'O:/02_Inputs/Aster/Bend/Inputs/Landsat_Thermal/Landsat_LPGS_B60_Stack.img'
array = raster(image)
info = raster_info(image)
coords = info['coords']
print coords
width = info['res'] * info['width']
height = info['res'] * info['height']

map = Basemap(projection = 'aea', lat_0 = 50, lon_0= -100, width = width * 3, height = height *3, resolution = 'h', area_thresh = 100.)
map.drawcoastlines()
map.bluemarble()
plt.imshow(array)
plt.show()
