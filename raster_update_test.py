from r_numpy_lib import *
Dir = 'A:/IansPlayground/FID_8/'
sr = Dir+ 'Burt_Adelson_Mosaic.img'
lr= Dir+ 'conus_with_defects_burn_into.img'
lrc = os.path.splitext(lr)[0] + '_copy.img'
if os.path.exists(lrc) == False:
    shutil.copy(lr,lrc)
burn_in_raster(sr,lrc,0.0001)