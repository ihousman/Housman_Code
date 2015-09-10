from r_numpy_lib import *

Dir = 'S:/WV2/Georeference/'
in_image = Dir + 'sept_30_2011_georef_nn.img'
out_image = Dir + 'sept_30_2011_georef_nn_aggregate_10py_wnd.img'
aggregate_raster(in_image, out_image,5,True)
