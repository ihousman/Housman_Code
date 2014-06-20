from r_numpy_lib import *


Dir = 'R:/NAFD/Landtrendr/LT_lite/gui_outputs_test/'
study_area = Dir + 'select_test1_slope.img'
output = Dir + 'test_dem.img'
dem_clip(study_area, output, zone = '16')
#reproject(study_area, output, zone = '16')
