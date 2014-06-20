from r_numpy_lib import *



DEM = '//166.2.126.25/R4_VegMaps/Misc_DataLayers/US_DEM/big_dem.img'

Dir = 'H:/6Tool_Comparison/'
SA = Dir + 'Study_Areas/Canaan_WV.shp'

out_dem = Dir + 'DEMs/Canaan_WV_DEM.img'
clip_by_shapefile(SA, DEM, out_dem)
