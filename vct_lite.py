#This script was written by Ian Housman at the Forest Service Remote Sensing Applications Center
#ihousman@fs.fed.us
#Funding was originally provided by the remote sensing steering committee for creation of this script
############################################

from r_numpy_lib import *
import os, sys, shutil
############################################
cwd = os.getcwd()
parts = cwd.split('\\')
cwd = ''
for part in parts:
    cwd += part + '/'
#############################################
def cleanup(Dir):
    for File in os.listdir(Dir):
        print 'Removing', File
        try:
            os.remove(Dir + '/' + File)
        except:
            print 'Could not remove', File
############################################
#Set up the proper file paths
nas_dir = 'O:/02_Inputs/Thermal_Prep/'
local_dir = 'C:/NAFD/VCT/'
pr = '1937'
anc_dir = 'ancData/'
glovis_dir = 'glovis/'
temp_dir = 'temp/'
quick_lk = 'quick_look/'
clean = False
nas_glovis_dir = nas_dir + pr + '/' + glovis_dir
nas_anc_dir = nas_dir + pr + '/' + anc_dir
nas_temp_dir = nas_dir + pr + '/' + temp_dir
local_glovis_dir = local_dir + glovis_dir
local_temp_dir = local_dir + temp_dir
local_anc_dir = local_dir + anc_dir
quick_look_dir = local_dir + quick_lk
#########################################
if os.path.exists(local_temp_dir) == False:
    os.makedirs(local_temp_dir)
if os.path.exists(nas_temp_dir) == False:
    os.makedirs(nas_temp_dir)
if os.path.exists(quick_look_dir) == False:
    os.makedirs(quick_look_dir)
if os.path.exists(local_anc_dir) == False:
    os.makedirs(local_anc_dir)
if os.path.exists(local_glovis_dir) == False:
    os.makedirs(local_glovis_dir)
if clean == True:
    cleanup(local_anc_dir)
    cleanup(local_glovis_dir)
    cleanup(local_temp_dir)

########################################
#Unzip one band from tarball
files = glob_find(nas_glovis_dir, '.tar')
File = files[0]
temps = glob(local_temp_dir, '.TIF')

if len(temps) == 0:
    print 'Untaring single band to serve as path/row footprint'
    TIFs =untar(File, local_temp_dir, [3])
else:
    TIFs = [temps[0]]
TIF = TIFs[0]
########################################
#Prepares the ancillary data
#Clips/reprojects NLCD data and DEM data
#DEM data may have gaps in it due to GDAL's reprojecting tiling
def anc_prep(pr = pr, template = TIF):
    pr_long = '0' + pr[:2] + '0' + pr[2:]
    print pr_long
    dem = local_temp_dir + pr_long + '_dem.img'
    nlcd = local_temp_dir + pr_long + '_nlcd.img'
    dem_envi = local_anc_dir + os.path.splitext(os.path.basename(dem))[0]
    nlcd_envi = local_anc_dir + os.path.splitext(os.path.basename(nlcd))[0]
    if os.path.exists(nlcd) == False:
        nlcd_clip(template, nlcd, res = '30', datum = 'WGS84', mask_output = False)
    if os.path.exists(dem) == False:
        dem_clip(template, dem, res = '30', datum = 'WGS84', mask_output = False, dt = 'Int16')
    if os.path.exists(nlcd_envi) == False:    
        convert(nlcd, nlcd_envi, Format = 'ENVI')
        make_vct_header(nlcd_envi)
    if os.path.exists(dem_envi) == False:
        convert(dem, dem_envi, Format = 'ENVI')
        make_vct_header(dem_envi)
########################################
def move_tarballs():
    #Move tarballs
    files = glob_find(nas_glovis_dir, '.tar')
    for File in files:
        
        local_tar = local_glovis_dir + os.path.basename(File)
        if os.path.exists(local_tar) == False:
            print 'Copying', os.path.basename(File), 'to local glovis dir'
            shutil.copy(File, local_tar)
        else:
            print 'Already copied', os.path.basename(File)
########################################
#Function to run VCT
#Sets up a script dictionary to provide path to individual VCT components
def run_vct(pr,
            glovis_dir = 'C:/NAFD/VCT/glovis',
            bat_file = os.path.dirname(local_glovis_dir) + '/vct_lite_bat.bat',run_scripts = ['convert_script', 'clip_mask_toa_script', 'fix_bat_script', 'callud_script'],
            script_dict = {'convert_script' : ['C:/NAFD/VCT/vctTools/landsat/convertGeoTiff2Envi.py', 'glovis_dir', ' ', 'glovis_dir'],
                           'clip_mask_toa_script' : ['C:/NAFD/VCT/vctTools/clipMaskToa.exe', 'glovis_dir', 'pr_long', '_imagelist.txt' ],
                           'fix_bat_script' : ['C:/NAFD/VCT/vctTools/vct_edit_bat2.py',''],
                           'callud_script' : ['cd C:/NAFD/VCT\nC:\NAFD\VCT/callUd.bat','']
                           },
            var_list = ['glovis_dir', 'pr_long']):
    pr_long = '/p0' + pr[:2] + 'r0' + pr[2:]
    bat_lines = []
    for script in run_scripts:
        call = script_dict[script][0] + ' '
      
        for call_piece in script_dict[script][1:]:
            if call_piece in var_list:
                call += eval(call_piece)
               
            else:
                call += call_piece
        print 'Calling:', call
        bat_lines.append(call + '\n')
        #c = subprocess.Popen(call)
        #c.wait()
        print
        print
    open_file = open(bat_file, 'w')
    open_file.writelines(bat_lines)
    open_file.close()
    call = subprocess.Popen(bat_file)
    call.wait()
########################################
def upload_and_convert():
    batch_convert(local_glovis_dir, nas_glovis_dir)
    batch_convert(local_anc_dir, nas_anc_dir)
    batch_convert(local_temp_dir, nas_temp_dir, convert_from_extension = '.img',out_format = 'HFA')
########################################

#quick_look(files, quick_look_dir)
#anc_prep(pr)
#move_tarballs()
#run_vct(pr)
#upload_and_convert()




##

#Relic code from thermal project
##files = filter(lambda i : i.find('_toa.tif') > -1, os.listdir(nas_glovis_dir))
##files = map(lambda i : nas_glovis_dir + i, files)
##for File in files:
##    output = os.path.splitext(File)[0] + '_B60_VCT.img'
##    restack(File, output, File, [7])
