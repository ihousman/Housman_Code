#Import all necessary packages
import shutil, os, subprocess, sys, string, random, math, time, itertools, urllib, zipfile
#Set Python version
python_possibilities = {'C:\\Python26\\ArcGIS10.0': [26, 10], 'C:\\Python26': [26, 9.3],'C:\\Python25' : [25, 9.3]}
for possibility in python_possibilities:
    if os.path.exists(possibility):
        arc_version = python_possibilities[possibility][1]
        python_version =   python_possibilities[possibility][0]
        python_dir = possibility
        break
print 'Arc version:',arc_version
print 'Python version:', python_version
print 'Python dir:', python_dir
#arc_version =9.3
#python_version = 26
python_version_dec = str(float(python_version)/10)
python_version = str(python_version)
admin = False
program_files_dir_options = ['C:/Program Files (x86)/', 'C:/Program Files/']
for option in program_files_dir_options:
    if os.path.exists(option):
        program_files_dir = option
        break
print 'Program files dir:', program_files_dir

gdal_dir = program_files_dir + 'FWTools2.4.7/bin/'

#Reprojects a raster using gdalwarp
#Will produce lines with zero values if RMSE is high
#Can specify the crs manually as a string, only define the necessary parts of a UTM coordinate system, or define the proj = 'Albers' for albers
#resampling_method:  near (default), bilinear, cubic, cubicspline, lanczos
#clip_extent: 'xmin ymin xmax ymax'
def reproject(Input, output, crs = '', proj = 'utm', zone = '', datum = 'nad83' , res = '',resampling_method = 'cubic', clip_extent = '', no_data = '', Format = 'HFA', dt = '', gdal_dir = program_files_dir + 'FWTools2.4.7/bin/'):
    if type(Input) == list:
        temp = Input
        Input = ''
        for t in temp:
            Input += t + ' '
        Input = Input[:-1]
    if proj == 'albers' or proj == 'Albers' or proj == 'albers_conical':
        #Use for USA Contiguous Albers Equal Area Conic USGS.prj
        #Same as in MTBS .prj file:
        #PROJCS["USA_Contiguous_Albers_Equal_Area_Conic_USGS_version",GEOGCS["GCS_North_American_1983",
        #DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],
        #UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],
        #PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-96.0],PARAMETER["Standard_Parallel_1",29.5],
        #PARAMETER["Standard_Parallel_2",45.5],PARAMETER["Latitude_Of_Origin",23.0],UNIT["Meter",1.0]]
        crs = '"+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs +towgs84=0,0,0"'
    #lambert_list = 
    elif proj in ['laea', 'lamberts', 'lambert']:
        crs = '"+proj=laea +lat_0=45 +lon_0=-100 +x_0=0 +y_0=0 +a=6370997 +b=6370997 +datum=NAD83 +ellps=GRS80 +units=m +no_defs"'
    if crs == '' and zone != '':
        crs = ' -t_srs "+proj=' + proj + ' +zone=' + str(zone) + ' +datum=' + str(datum) + '"'
    elif crs != '':
        crs += ' -t_srs ' + crs
    
    if res != '':
        res = ' -tr ' + str(res) + ' ' + str(res) + ' '
    
    if no_data != '':
        no_data = ' -srcnodata ' + str(no_data) + ' -dstnodata '+ str(no_data)
    if clip_extent != '':
        clip_extent = ' -te ' + clip_extent
    if dt != '':
        dt = ' -ot ' + str(dt) + ' '
    print 'Reprojecting:' ,Input.split('/')[-1]
    print
    if Format != '':
        ot = ' -of ' + Format 
    gdal_call = gdal_dir + 'gdalwarp' + ot + dt+ no_data  + crs + res + clip_extent +' -r ' + resampling_method + ' ' + Input + ' ' + output
    print gdal_call
    print
    call = subprocess.Popen(gdal_call)
    call.wait()
########################################################################################################################
