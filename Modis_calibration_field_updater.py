import os, sys, math, random, string, shutil
from dbfpy import dbf
r_numpy_dir ='E:/Thermal_Mapping/R/Scripts/VB/Tools/'

if r_numpy_dir not in sys.path:
    print 'Adding', r_numpy_dir,'to path list'
    sys.path.append(r_numpy_dir)
from r_numpy_lib import *
###############################################################################
cwd = os.getcwd()
parts = cwd.split('\\')
cwd = ''
for part in parts:
    cwd += part + '/'
############################################################################
############################################################################
#root = '//166.2.126.25/rseat/Programs/RSSC/fy2012/Projects/10025_R&D_Thermal_Mapping/02_Data-Archive/02_Inputs/'
root = 'O:/02_Inputs/'
city = 'Atlanta'
sensor = 'MODIS'
datum = 'NAD83'
calibration_field = 'PCT_IMPV'
combo_range = range(2,5)
zone_dict = {'Atlanta': 17, 'Baltimore' : 18}
res_dict = {'Aster': 90, 'MODIS' : 1000}
res = res_dict[sensor]
zone = zone_dict[city]
############################################################################
############################################################################
inputs_dir = root + sensor + '/' + city + '/Inputs/'
outputs_dir = root + sensor + '/' + city + '/Outputs/'
calibration_dir = inputs_dir + 'Calibration/'
l_spectral_dir = inputs_dir + 'Landsat_Spectral/'
l_thermal_dir = inputs_dir + 'Landsat_Thermal/'
nlcd_dir = inputs_dir + 'NLCD/'
terrain_dir = inputs_dir + 'Terrain/'
thermal_dir = inputs_dir + 'Thermal/'
mask_dir = inputs_dir + 'Mask/'
anc_master = root + 'Ancillary/Rasters/'
############################################################################
from_file = calibration_dir + 'RSAC-Atlanta2006-Total.txt'
to_file = calibration_dir + 'Atlanta_Modis_Training_Sample.shp'
open_file = open(from_file, 'r')
lines = open_file.readlines()
open_file.close()
update_list = []
for Line in lines[1:]:
    Line = Line.split('\t')
    Line[-1] = Line[-1][:-1]
    
    update_list.append(float(Line[-1]))#* 100)
print len(update_list)

#add_field(to_file, 'PCT_IMPV', 'Real')
update_field(to_file, 'PCT_IMPV', update_list)
