from r_numpy_lib import *
import os, sys, shutil
from numpy import *
############################################
cwd = os.getcwd()
parts = cwd.split('\\')
cwd = ''
for part in parts:
    cwd += part + '/'
#############################################
#############################################
def cleanup(Dir):
    for File in os.listdir(Dir):
        print 'Removing', File
        try:
            os.remove(Dir + '/' + File)
        except:
            print 'Could not remove', File
############################################
def thermal_correction_Ohio_State(Landsat_TM_b6, output, t_band = 1):
    #Source: http://hcgl.eng.ohio-state.edu/~cenr797/pdf/Exercise3.pdf
    #info = raster_info(Landsat_TM_b6)
    if os.path.exists(output) == False or overwrite == True:
        try:
            
            array = raster(Landsat_TM_b6, dt = 'Float32', band_no = t_band)
            out_array = (1282.71/numpy.log( (666.09/ ((((12.65-3.2)/255.0) *array) +3.2)   )+1.0 ))-273
            
            write_raster(out_array, output, Landsat_TM_b6, dt = 'Float32')
        except:
            array = None
            out_array = None
    
    array = None
    out_array = None
############################################
def LPGS_thermal_Correction_L5(Landsat_TM_b6, output, t_band = 1, overwrite = False):
    #Source: USGS LPGS models
    n6_Float = 0.055158
    n7_Float = 1.2378
    n8_Float = 607.76
    n9_Float = 1260.56
    if os.path.exists(output) == False or overwrite == True:
        try:
            array = raster(Landsat_TM_b6, dt = 'Float32', band_no = t_band)

            out_array = ((n9_Float / (numpy.log(n8_Float/(n6_Float * array + n7_Float)+ 1)))-240.0) * 3.0
            
            write_raster(out_array, output, Landsat_TM_b6, dt = 'Float32')
        except:
            array = None
            out_array = None
    array = None
    out_array = None
############################################
nas_dir = 'O:/02_Inputs/Thermal_Prep/'
local_dir = 'C:/NAFD/VCT/'
pr = '1937'
anc_dir = 'ancData/'
glovis_dir = 'glovis/'
temp_dir = 'temp/'
clean = False
tir_band = 5
year_list = ['2006']
nas_glovis_dir = nas_dir + pr + '/' + glovis_dir
nas_anc_dir = nas_dir + pr + '/' + anc_dir
nas_temp_dir = nas_dir + pr + '/' + temp_dir
local_glovis_dir = local_dir + glovis_dir
local_temp_dir = local_dir + temp_dir
local_anc_dir = local_dir + anc_dir
#########################################
########################################
#Move tarballs
files = filter(lambda i: os.path.splitext(i)[1] == '.gz', os.listdir(nas_glovis_dir))
files = map(lambda i : nas_glovis_dir + i, files)
TIFs = []
for File in files:
    local_File = local_glovis_dir + os.path.basename(File)
    if os.path.exists(local_File)== False:
        print 'Copying', os.path.basename(File), 'to local glovis dir'
        shutil.copy(File, local_File)



temps = filter(lambda i: os.path.splitext(i)[1] == '.TIF', os.listdir(local_temp_dir))
temps = map(lambda i : local_temp_dir + i, temps)
year_date_list = []
for temp in temps:
    for year in year_list:
        if len(temp.split(str(year))) > 1:
            break
    date = temp.split(year)[1][:4]
    year_date_list.append([str(year), str(date)])

for File in files:
    print File
    for year in year_list:
        if len(os.path.basename(File).split(str(year))) > 1:
            break
    date = os.path.basename(File).split(str(year))[1][:3]
    date = julian_to_calendar(date, year)['monthdate']
    if [year, date] not in year_date_list:
        untar(File, local_temp_dir, [tir_band])

temps = filter(lambda i: os.path.splitext(i)[1] == '.TIF' and i.find('B40') == -1, os.listdir(local_temp_dir))
temps = map(lambda i : local_temp_dir + i, temps)
print len(temps), len(files)
for temp in temps:
    output = os.path.splitext(temp)[0] + '_t_calc4.img'
    lpgs_output = os.path.splitext(temp)[0] + '_LPGS.img'
    #thermal_correction_Ohio_State(temp, output)
    LPGS_thermal_Correction_L5(temp, lpgs_output)


