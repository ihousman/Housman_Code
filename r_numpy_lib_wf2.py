#This script contains a library of functions that use various open source statistical and geospatial
#software packages to ease basic raster processing and modeling procedures
#This script was written with funding from a USDA Forest Service Remote Sensing
#Steering Commmittee project that used thermal data to model percent impervious

#This script was written by Ian Housman at the Forest Service Remote Sensing Applications Center
#ihousman@fs.fed.us
###############################################################################
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


if os.path.exists(python_dir)==False:
    print 'Python version:', python_version, 'Arc version:', arc_version,'does not exist'
    raw_input('Press enter to exit')
    sys.exit()


try:
    from tarfile import TarFile
except:
    import tarfile
###############################################################################
cwd = os.getcwd()
parts = cwd.split('\\')
cwd = ''
for part in parts:
    cwd += part + '/'
###############################################################################

from tkFileDialog import askopenfilename
from tkFileDialog import askopenfilenames
from tkFileDialog import askdirectory
from tkSimpleDialog import askstring
from tkMessageBox import showwarning
import tkMessageBox
from tkFileDialog import asksaveasfilename

##################################################################
def install(package_name, cleanup = False):
    install_packages = {'dbfpy':['http://sourceforge.net/projects/dbfpy/files/dbfpy/2.2.5/dbfpy-2.2.5.win32.exe/download', 'dbfpy-2.2.5.win32.exe'],
                        'numpy': ['http://sourceforge.net/projects/numpy/files/NumPy/1.6.1/numpy-1.6.1-win32-superpack-python'+python_version_dec+'.exe/download','numpy-1.6.1-win32-superpack-python'+python_version_dec+'.exe'],
                        'gdal' : ['http://pypi.python.org/packages/'+python_version_dec+'/G/GDAL/GDAL-1.6.1.win32-py'+python_version_dec+'.exe#md5=5e48c85a9ace1baad77dc26bb42ab4e1','GDAL-1.6.1.win32-py'+python_version_dec+'.exe'],
                        'rpy2' : ['http://pypi.python.org/packages/'+python_version_dec+'/r/rpy2/rpy2-2.0.8.win32-py'+python_version_dec+'.msi#md5=2c8d174862c0d132db0c65777412fe04','rpy2-2.0.8.win32-py'+python_version_dec+'.msi'],
                        'r11'    : ['http://cran.r-project.org/bin/windows/base/old/2.11.1/R-2.11.1-win32.exe', 'R-2.11.1-win32.exe'],
                        'r12'    : ['http://cran.r-project.org/bin/windows/base/old/2.12.1/R-2.12.1-win.exe', 'R-2.12.1-win32.exe'],
                        'fw_tools' : ['http://home.gdal.org/fwtools/FWTools247.exe', 'FWTools247.exe'],
                        'matplotlib' : ['http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.1.1/matplotlib-1.1.1rc.win32-py2.6.exe', 'matplotlib-1.1.1rc.win32-py2.6.exe'],
                        'scipy' : ['http://sourceforge.net/projects/scipy/files/scipy/0.10.1/scipy-0.10.1-win32-superpack-python'+python_version_dec+'.exe', 'scipy-0.10.1-win32-superpack-python'+python_version_dec+'.exe'],
                        'gdalwin32':['http://download.osgeo.org/gdal/win32/1.6/gdalwin32exe160.zip', 'ggdalwin32exe160.zip'],
                        'pywin32' : ['http://sourceforge.net/projects/pywin32/files/pywin32/Build%20217/pywin32-217.win32-py'+python_version_dec+'.exe','pywin32-217.win32-py'+python_version_dec+'.exe']
                        }
    #extensions = {'dbfpy':'.exe','numpy': '.exe','gdal' : '.exe','rpy2' : '.msi'}
             
    url = install_packages[package_name][0]
    exe = cwd + '/'+install_packages[package_name][1]
    if os.path.exists(exe) == False:
        print 'Downloading', os.path.basename(exe)
        File = urllib.urlretrieve(url, exe)
    if os.path.splitext(exe)[1] != '.zip':
        print 'Installing', package_name
        try:
            call = subprocess.Popen(exe)
        except:
            print 'Running .msi', exe
            call = subprocess.Popen('msiexec /i ' + os.path.basename(exe))
        call.wait()
    else:
        print 'its a zip'
        Zip = zipfile.ZipFile(exe)
        Zip_names = Zip.namelist()
        print Zip_names
        for name in Zip_names:
            
            if os.path.splitext(name)[1] == '':
                try:
                    if os.path.exists(cwd + name) == False:
                        os.makedirs(cwd + name)
                except:
                    print 'oops'
        Zip.extractall(cwd)
    if cleanup == True:
        try:
            os.remove(exe)
        except:
            print 'Could not remove:', os.path.basename(exe)

##################################################################
#Function to install any r packages
#Can provide a single name of a library or a list of names of libraries to install
def r_library_installer(lib_list = '', cran = 'local({r <- getOption("repos")\nr["CRAN"] <- "http://cran.stat.ucla.edu"\noptions(repos=r)})', guiable = True):
    if lib_list == '':
        lib_list = askstring('Message','Please enter an r library to install')
    r(cran)
    if lib_list != list:
        lib_list = [lib_list]
   
    for lib in lib_list:
        print 'Installing:', lib
        try:
            r('install.packages("' + lib + '")')
        except:
            print 'Could not install:', lib

#############################################################################
            
try:
   
    path = os.environ.get('PATH')
    if path[-1] != ';':
        path += ';'
   
    path = path + python_dir+'\\Lib\\site-packages\\gdalwin32-1.6\\bin'
    os.putenv('GDAL_DATA',python_dir+'\\Lib\\site-packages\\gdalwin32-1.6\\data')
    os.putenv('PATH',path)
    
    from osgeo import gdal
    from osgeo import gdal_array
    from osgeo import osr, ogr
    
except:
    
    admin = tkMessageBox.askyesno('Administrator','Are you an administrator?')
    if admin:
 #       install('gdalwin32')
        install('gdal')
        install('pywin32')
        install('numpy')
        path = os.environ.get('PATH')
        if path[-1] != ';':
            path += ';'
        
        path = path + python_dir+'\\Lib\\site-packages\\gdalwin32-1.6\\bin'
        os.putenv('GDAL_DATA',python_dir+'\\Lib\\site-packages\\gdalwin32-1.6\\data')
        os.putenv('PATH',path)
        
        try:
            from osgeo import gdal
            from osgeo import gdal_array
            from osgeo import osr, ogr
        except:
            print 'Installation of gdal/osgeo was unsuccessful'
            print 'Please search for GDAL-1.6.1.win32-py'+python_version_dec+'.exe and manually install'
            raw_input('Press enter to exit')
            sys.exit()
    else:
        tkMessageBox.showinfo('Administrator','You must be administrator to install the software.')
        sys.exit()
##################################################################
try:
    import numpy
    from numpy import numarray
    try:
        from numpy.numarray import nd_image
    except:
        print 'Cannot use nd_image functions'
except:
    install('numpy')
    try:
        import numpy
        from numpy import numarray
        from numpy.numarray import nd_image
    except:
        print 'Installation of numpy was unsuccessful'
        print 'Please search for numpy and manually install'
        raw_input('Press enter to exit')
        sys.exit()

####################################################################
try:
    from dbfpy import dbf
except:
    install('dbfpy')
    print 'Could not find dbfpy'
    
    
    try:
        from dbfpy import dbf
        print 'Successfully installed dbfpy'
    except:
        print 'Installation of dbfpy was unsuccessful'
        print 'Please search for dbfpy and manually install'
        raw_input('Press enter to exit')
##################################################################
if os.path.exists(gdal_dir) == False:
    install('fw_tools')
####################################################################    
try:
    if path[-1] != ';':
        path += ';'
    #r_home = 'C:\\Program Files (x86)\\R\R-2.11.1\\bin'
    win32com_path = python_dir + 'Lib\\site-packages\\win32'
    sys.path.append(win32com_path)
    #path = path + r_home
    #os.putenv('PATH',path)
    #os.putenv('R_HOME',r_home)
    
    import rpy2.robjects as RO
    import rpy2.robjects.numpy2ri
    r = RO.r
except:
    print 'Could not find rpy2'
    if admin == False:
        admin = tkMessageBox.askyesno('Administrator','Are you an administrator?')
    if admin:
    
        install('r11')
        install('rpy2')
        
        try:
            import rpy2.robjects as RO
            import rpy2.robjects.numpy2ri
            r = RO.r
            lib_list = ['rgdal', 'raster', 'maptools', 'randomForest']
            for lib in lib_list:
                try:
                    r.library(lib)
                except:
                    print 'Installing:', lib
                    r_library_installer([lib])
        except:
            print 'Installation of rpy2 was unsuccessful'
            print 'Please search for rpy2 and manually install'
            raw_input('Press enter to exit')
            sys.exit()
    else:
        tkMessageBox.showinfo('Administrator','You must be administrator to install the software.')
            #sys.exit()


##################################################################
try:
    from Rscript import *

    r_dir = program_files_dir + 'R/R-2.12.1/bin/'
    if os.path.exists(r_dir) == False:
        warning = showwarning('!!!MUST READ!!!!', 'In the "Select Additional Tasks" window, ensure that the "Save version number in registry" option is unchecked\n'\
                              'The script will not run properly if left checked')
        r1 = R()
        r1 = None
except:
    print 'Cannot use Rscript module'
##################################################################
#Function to load r library using rpy2
#Calls on installer if the library does not exist
def r_library_loader(lib_list = '', guiable = True):
    if lib_list == '':
        lib_list = askstring('Message','Please enter an r library to load')
    if type(lib_list) != list:
        lib_list = [lib_list]
    for lib in lib_list:
        
        try:
            print 'Loading:', lib
            r.library(lib)
        except:
            print 'Installing:', lib
            r_library_installer(lib)
            print
            print 'Loading:', lib
            r.library(lib)
##################################################################
#Status bar function that prints the percent of the total list that has been looked at
#last variable must be seeded and then passed in within the loop in order to prevent printing due to rounding
def status_bar(current_index, list_length, percent_interval = 5, last = 0):
    divisor = 100/ percent_interval
    interval = list_length / divisor
    percent_list = range(0, 100, percent_interval)
    current_percent =  int(float(current_index)/ float(list_length) * 100)
    
    if int(current_percent) in percent_list and current_percent != last:
        last = current_percent
        print str(current_percent) +'%',
    return last
##############################################################################################
def sort(in_list, order = range(1000), num_break = '_', num_place = 0, simple = True):
    out_list = []
    
    for num in order:
        for entry in in_list:
            if simple == False:
                if str(num) == entry.split(num_break)[num_place]:
                    out_list.append(entry)
            else:
                if int(num) == int(entry):
                    out_list.append(int(entry))
    return out_list
##############################################################################################
def sort_by_column(in_2d_list, order = range(1000), column_no = 0):
    out_list = []
    
    for num in order:
        for entry in in_2d_list:
           
            if int(num) == int(entry[column_no]):
                out_list.append(entry)
    return out_list
############################################################################
def invert_list(in_list):
    out_list = [0] * len(in_list)
    
    for i in range(1, len(in_list)):
        out_list[-i] = in_list[i]
    out_list.pop(0)
    out_list.append(in_list[0])
    return out_list
############################################################################
def unique_count(in_list):
    set_list = list(set(in_list))
    out_list = []
    for part in set_list:
        counter = 0
        for line in in_list:
            if line == part:
                counter += 1
        out_list.append([part, counter])
    out_list = invert_list(sort_by_column(out_list, column_no = 1))
    return out_list
 
############################################################################
#Converts utm coordinates to geographic coordinates
#Code not written at RSAC
#Code source: http://stackoverflow.com/questions/343865/how-to-convert-from-utm-to-latlng-in-python-or-javascript
#Code foundation: http://www.ibm.com/developerworks/java/library/j-coordconvert/index.html
def utm_to_geog(zone = '', easting = '', northing = '', northernHemisphere=True, guiable = True, echo = False):
    if zone == '':
        zone = int(askstring('Zone Entry','Enter UTM zone number: '))
    if easting == '':
        easting = float(askstring('Easting Entry','Enter UTM easting: '))
    if northing == '':
        northing = float(askstring('Northing Entry','Enter UTM northing: '))
        
    if not northernHemisphere:
        northing = 10000000 - northing
    northing = float(northing)
    easting = float(easting)
    zone = int(zone)
    a = 6378137
    e = 0.081819191
    e1sq = 0.006739497
    k0 = 0.9996

    arc = northing / k0
    mu = arc / (a * (1 - math.pow(e, 2) / 4.0 - 3 * math.pow(e, 4) / 64.0 - 5 * math.pow(e, 6) / 256.0))

    ei = (1 - math.pow((1 - e * e), (1 / 2.0))) / (1 + math.pow((1 - e * e), (1 / 2.0)))

    ca = 3 * ei / 2 - 27 * math.pow(ei, 3) / 32.0

    cb = 21 * math.pow(ei, 2) / 16 - 55 * math.pow(ei, 4) / 32
    cc = 151 * math.pow(ei, 3) / 96
    cd = 1097 * math.pow(ei, 4) / 512
    phi1 = mu + ca * math.sin(2 * mu) + cb * math.sin(4 * mu) + cc * math.sin(6 * mu) + cd * math.sin(8 * mu)

    n0 = a / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (1 / 2.0))

    r0 = a * (1 - e * e) / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (3 / 2.0))
    fact1 = n0 * math.tan(phi1) / r0

    _a1 = 500000 - easting
    dd0 = _a1 / (n0 * k0)
    fact2 = dd0 * dd0 / 2

    t0 = math.pow(math.tan(phi1), 2)
    Q0 = e1sq * math.pow(math.cos(phi1), 2)
    fact3 = (5 + 3 * t0 + 10 * Q0 - 4 * Q0 * Q0 - 9 * e1sq) * math.pow(dd0, 4) / 24

    fact4 = (61 + 90 * t0 + 298 * Q0 + 45 * t0 * t0 - 252 * e1sq - 3 * Q0 * Q0) * math.pow(dd0, 6) / 720

    lof1 = _a1 / (n0 * k0)
    lof2 = (1 + 2 * t0 + Q0) * math.pow(dd0, 3) / 6.0
    lof3 = (5 - 2 * Q0 + 28 * t0 - 3 * math.pow(Q0, 2) + 8 * e1sq + 24 * math.pow(t0, 2)) * math.pow(dd0, 5) / 120
    _a2 = (lof1 - lof2 + lof3) / math.cos(phi1)
    _a3 = _a2 * 180 / math.pi

    latitude = 180 * (phi1 - fact1 * (fact2 + fact3 + fact4)) / math.pi

    if not northernHemisphere:
        latitude = -latitude

    longitude = ((zone > 0) and (6 * zone - 183.0) or 3.0) - _a3
    if echo == True:
        print 'Latitude:', latitude
        print 'Longitude:', longitude
    return latitude, longitude
##############################################################################################
#Converts utm coord list (xmin, ymin, xmax, ymax) to geographic based on a specified zone
def utm_coords_to_geographic(coords, zone):
    coords1 = utm_to_geog(zone, coords[0], coords[1])
    coords2 = utm_to_geog(zone, coords[2], coords[3])
    out = [coords1[1], coords1[0], coords2[1], coords2[0]]
    return out
##############################################################################################
#Converts between Numpy and GDAL data types
#Will automatically figure out which direction it must go (numpy to gdal or gdal to numpy)
def dt_converter(dt):
    Dict = {'u1': 'Byte', 'uint8' : 'Byte', 'uint16': 'UInt16','u2': 'UInt16', 'u4': 'UInt32', 'i2' : 'Int16', 'int16':'Int16', 'Float32' : 'float32','float32' : 'Float32', 'Float64' : 'float64','float64' : 'Float64'}
    try:
        Type = Dict[dt]
    except:
        Dict = dict(map(lambda a:[a[1], a[0]], Dict.iteritems()))
        Type = Dict[dt]
    return Type
##############################################################################################
#Finds the data type of an image
#Returns the gdal data type
def dt_finder(image):
    rast = gdal.Open(image)
    band1 = rast.GetRasterBand(1)
    dt = band1.DataType
    rast = None
    band1 = None
    Dict = {1: 'Byte', 2 : 'UInt16', 3: 'Int16', 4: 'UInt32', 5: 'Int32', 6 : 'Float32'}
    dataType = Dict[dt]
    return dataType 
##############################################################################################
#Converts between common projection formats
#Returns a dictionary containing the wkt and proj4 formats
def projection_format_converter(projection, Format = 'Wkt'):
    spatialRef = osr.SpatialReference()
    eval('spatialRef.ImportFrom'+Format+'(projection)')
    proj4 = spatialRef.ExportToProj4()
    wkt = spatialRef.ExportToWkt()
    return {'proj4' : proj4, 'wkt': wkt, 'spatialRef' : spatialRef}
##############################################################################################
#Buffers coordinates a specified distance
#Input must be projected, but can product geographic coordinates with UTM input
def buffer_coords(coords, Buffer = 1000, geographic = False, zone = ''):
    out_coords = [coords[0] - Buffer, coords[1] - Buffer, coords[2] + Buffer, coords[3] + Buffer]
    if geographic == True:
        out_coords =  utm_coords_to_geographic(out_coords, zone)
    return out_coords
##############################################################################################
def coords_to_gdal(coords):
    return str(coords[0]) + ', ' + str(coords[1]) + ', ' + str(coords[2]) + ', ' + str(coords[3])
##############################################################################################
#Gathers various information about a shapefile and returns it in a dictionary
def shape_info(shapefile, runr = False):
##    r('library(maptools)')
##    r('shp = readShapeSpatial("' + shapefile + '")')
##    r('bbox = data.frame((summary(shp)[2]))')
##    bbox = r('bbox')
##    r('print(summary(shp))')
    proj4 = ''
    if runr == True:
        r('library(rgdal)')
        r('shp = readOGR("' + shapefile + '", "' + os.path.splitext(shapefile)[0].split('/')[-1] + '")')
        proj4string = r('as.character(proj4string(shp))')
        proj4 = str(proj4string[0])
        #print proj4
    prj_filename = os.path.splitext(shapefile)[0] + '.prj'
    shp = ogr.Open(shapefile)
    lyr = shp.GetLayerByName(os.path.splitext(shapefile)[0].split('/')[-1])
    
    
    extent = list(lyr.GetExtent())
    numFeatures = lyr.GetFeatureCount()
    projection = lyr.GetSpatialRef()
    ESRI_projection = projection
    xmin = extent[0]
    xmax = extent[1]
    ymin = extent[2]
    ymax = extent[3]
    coords = [xmin,ymin,xmax,ymax]
    width = xmax - xmin
    height = ymax - ymin
    gdal_coords = str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax)
  

    
    if os.path.exists(prj_filename):
        prj_open = open(prj_filename)
        prj = prj_open.readlines()
        prj_open.close()
        try:
            if len(projection) > 1:
                projection =  prj[0].split('PROJCS["')[1].split('",')[0]
            else:
                projection = prj
        except:
            projection = prj
        
        try:
            zone = projection.split('Zone')[1].split(',')[0][1:3]
        except:
            try:
                zone = projection.split('zone ')[1][:2]
            except:
                try:
                    zone = projection.split('zone=')[1][:2]
                except:
                    if type(projection) == list:
                        try:
                            zone = projection[0].split('Zone_')[1][:2]
                        except:
                            zone = ''
                    else:
                        zone = ''
        
        if projection[:3] == 'NAD':
            datum = 'NAD83'
        elif projection[:3] == 'WGS':
            datum = 'WGS84'
        else:
            datum = ''
    if proj4 == '':
        crs = '+proj=utm +zone=' + zone + ' +ellps=' + datum + ' +datum='
        proj4 = prj
    else:
        crs = proj4
    
    projections = projection_format_converter(str(ESRI_projection), 'Wkt')
    
    shp = None
    lyr = None
    info = {'proj4': projections['proj4'], 'wkt': projections['wkt'], 'esri' : projection, 'width': width, 'height': height,'gdal_coords': gdal_coords, 'coords' : coords, 'feature_count': numFeatures, 'zone':zone, 'datum': datum, 'crs':crs, 'projection': projection}
    return info
##
    
##############################################################################################
#Converts a CSV to kml
def csv_to_kml(csv, kml, zone = '', utm_or_geog = 'utm',header = True):
    open_csv = open(csv, 'r')
    lines = open_csv.readlines()
    open_csv.close()
    ID = os.path.basename(csv)

    out_kml = '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document id="'+ID+'">\n<name>'+ID+'</name>\n'
    out_kml += '<Snippet></Snippet>\n<Folder id="FeatureLayer0">\n<name>'+ID+'</name>\n<Snippet></Snippet>\n'

    if header == True:
        lines = lines[1:]
    i = 1
    for line in lines:
        x = float(line.split(',')[0])
        y = float(line.split(',')[1][:-1])

        if utm_or_geog == 'utm':
            coords = utm_to_geog(zone, x, y)
        else:
            coords = [x, y]
        
        out_kml += '<Placemark>\n<name>'+str(i)+'</name>\n<styleUrl>#IconStyle00</styleUrl>\n<Snippet></Snippet>\n<Point>\n<extrude>0</extrude>\t<altitudeMode>relativeToGround</altitudeMode>\n'
        out_kml += '<coordinates> '+str(coords[1])+','+str(coords[0])+',0.000000</coordinates>\n</Point>\n</Placemark>\n'
        i += 1

    out_kml += '</Folder>\n<Style id="IconStyle00">\n<IconStyle>\n<Icon><href>000000.png</href></Icon>\n<scale>1.000000</scale>\n</IconStyle>\n<LabelStyle>\n<color>00000000</color>\n<scale>0.000000</scale>\n</LabelStyle>\n</Style>\n</Document>\n</kml>'

    out_open = open(kml, 'w')
    out_open.writelines(out_kml)
    out_open.close()
##############################################################################################
def range_to_dt(Min, Max):
    dt_ranges_int = [[[0, 256], 'Byte'], [[-32768, 32769], 'Int16'], [[0, 65536], 'Unt16'], [[0, 4294967296], 'UInt32']]
    dt_ranges_float = [[[-3.4E38, 3.4E38], 'Float32'], [[-1.7E308, 1.7E308], 'Float64']]

    print type(Min)
    
    type_dict = {float: 'float', int: 'int'}
    
    for Range in eval('dt_ranges_' + type_dict[type(Min)]):
        dt_range = Range[0]
        
        if Min  >= dt_range[0] and Max <= dt_range[1]:
            return Range[1]
            break
##############################################################################################
#Gathers various information about a raster and returns it in a dictionary
def raster_info(image = '', band_no = 1, get_stats = False, guiable = True):
    if image == '':
        guied = True
        image = str(askopenfilename(title = 'Select Strata Raster',filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
    else:
        guied = False
    print image
    rast = gdal.Open(image)
    band1 = rast.GetRasterBand(band_no)
    dt = band1.DataType
    if get_stats == True:
        stats = band1.GetStatistics(False,1)
        Min = stats[0]
        Max = stats[1]
        mean = stats[2]
        stdev = stats[3]
    else:
        Min, Max, mean, stdev = 0,0,0,0

    band1 = None
    Dict = {1: 'Byte', 2 : 'UInt16', 3: 'Int16', 4: 'UInt32', 5: 'Int32', 6 : 'Float32'}
    dataType = Dict[dt]
    dt_ranges = {'Byte': [0,255], 'Int16': [-32768, 32768], 'UInt16': [0,65535],'UInt32': [0,4294967295], 'Float32':[-3.4E38, 3.4E38],'Float64':[-1.7E308, 1.7E308]}
    dt_range = dt_ranges[dataType]
    
    width = rast.RasterXSize
    height = rast.RasterYSize
    
    
    bands = rast.RasterCount
    projection = rast.GetProjection()
    transform = rast.GetGeoTransform()
    transform = list(transform)
    projections = projection_format_converter(projection, 'Wkt')
    xmax = transform[0] + (int(round(transform[1])) * width)
    xmin = transform[0]
    ymax = transform[3] 
    ymin = transform[3]- (int(round(transform[1])) * height)
    
    coords = [xmin,ymin,xmax,ymax]
    gdal_coords = str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax)
    try:
        zone = projection.split('Zone')[1].split(',')[0][1:3]
    except:
        try:
            zone = projection.split('zone ')[1][:2]
        except:
            zone = ''

    datum_list = {'NAD':'NAD83', 'WGS':'WGS84'}
    try:
        datum = projection.split('GEOGCS["')[1].split('",')[0]
        if datum not in datum_list:
            for dat in datum_list:
                if datum.find(dat) > -1:
                    datum = datum_list[dat]
    except:
        datum = ''

    hemisphere = ''
    if (projection.find('North') > -1 or projection.find('north') > -1) and (projection.find('Hemisphere') > -1 or projection.find('hemisphere') > -1):
        hemisphere = 'North'
    else:
        hemisphere = 'South'


    units = ''
    if projection.find('meter') > -1 or projection.find('METER')> -1 or projection.find('Meter') > -1:
        units = 'Meters'
    res = transform[1]
    info = {'proj4': projections['proj4'], 'wkt': projections['wkt'], 'units': units, 'hemisphere' : hemisphere,'min': Min, 'max': Max, 'mean': mean, 'std':stdev, 'stdev':stdev, 'gdal_coords': gdal_coords, 'coords' : coords, 'projection':projection, 'transform': transform, 'width': width, 'height': height, 'bands': bands, 'band_count': bands, 'zone' : zone, 'datum': datum, 'res': res, 'resolution':res, 'dt_range': dt_range,'datatype': dataType, 'dt': dataType, 'DataType': dataType}
    if guied == True:
        for piece in info:
            print piece, info[piece]
    rast  = None
    return info
##############################################################################################
#Mr sid metadata extractor
def mr_sid_metadata(metadata_text_file):
    open_m = open(metadata_text_file, 'r')
    lines = open_m.readlines()
    open_m.close()

    find_list = ['West_Bounding_Coordinate', 'East_Bounding_Coordinate', 'North_Bounding_Coordinate', 'South_Bounding_Coordinate']
    out_dict = {}
    for Find in find_list:
        for line in lines:
            if line.find(Find) > -1:
                coord = line.split(':  ')[1].split('\n')[0]
                out_dict[Find.split('_')[0]] = coord
    coords = [float(out_dict['West']), float(out_dict['South']), float(out_dict['East']), float(out_dict['North'])]
    out_dict['coords'] = coords
    return out_dict
##############################################################################################
#Determines whether the data type is a numpy or gdal data type
def numpy_or_gdal(dt):
    numpy_list = ['u1', 'uint8', 'uint16','u2', 'u4', 'i2', 'int16', 'Float32','float32', 'Float64','float64']
    gdal_list = ['Byte', 'Byte', 'UInt16','UInt16','UInt32','Int16', 'Int16', 'float32','Float32','float64','Float64']
    dt_list = []
    if dt in numpy_list:
        dt_list.append('numpy')
    if dt in gdal_list:
        dt_list.append('gdal')
    if len(dt_list) == 2:
        return 'both'
    elif len(dt_list) == 1:
        return dt_list[0]
    else:
        return 'neither'
##############################################################################################
def julian_to_calendar(julian_date, year):
    julian_date = int(julian_date)
    year = int(year)
    leap_years = ['80', '84', '88', '92', '96', '00', '04', '08', '12', '16', '20', '24']
    year = str(year)[-2:]
    if year in leap_years:
        leap = True
        length = [31,29,31,30,31,30,31,31,30,31,30,31]
    else:
        leap = False
        length = [31,28,31,30,31,30,31,31,30,31,30,31]
    ranges = []
    start = 1
    for month in length:
        stop = start + month 
        ranges.append(range(start, stop))
        start = start + month
        
    month_no = 1
    for Range in ranges:
        if julian_date in Range:
            mn = month_no
            day_no = 1
            for day in Range:
                if day == julian_date:
                    dn = day_no
                day_no += 1
        month_no += 1
    if len(str(mn)) == 1:
        lmn = '0' + str(mn)
    else:
        lmn = str(mn)
    if len(str(dn)) == 1:
        ldn = '0' + str(dn)
    else:
        ldn = str(dn)
    return {'monthdate': lmn + ldn,'month':mn, 'day':dn, 'date_list': [mn,dn], 'date': str(mn) + '/' + str(dn)} 
##############################################################################################
#Untars Landsat TM (or any) tarball
def untar(tarball, output_dir = '', bands = []):
    if output_dir == '':
        output_dir = os.path.dirname(tarball) + '/'
    out_list = []
    out_folder = os.path.basename(tarball).split('.')[0].split('[')[0]
    
    if os.path.exists(output_dir + out_folder) == False:
        
        
        tar = TarFile.open(tarball, 'r:gz')
        if bands == []:
            print 'Unzipping:', os.path.basename(tarball) 
            #tar.extractall(path = output_dir)
        else:
            tar_names = tar.getnames()#[band]
            for band in bands:
                
                band = int(band)
                tar_name = tar_names[band]
                output_name = output_dir + tar_name
                out_list.append(output_name)
                if os.path.exists(output_name) == False:
                    print 'Unzipping:', output_dir + tar_name
                    tar.extract(tar_name, path = output_dir)
                
        tar.close()
    else:
        print 'Already unzipped:', os.path.basename(tarball)
    return out_list
##############################################################################################
#Will read a raster into a numpy array
#Returns a numpy array
#u1,u2,u4, i1,i2,i4, float32, float64
#Does not support < unsigned 8 byte
def raster(Raster, dt = '', band_no = 1, xoffset = 0, yoffset = 0, width = '', height = ''):
    info = raster_info(Raster)
    if dt == '':
        dt = info['dt']
    if numpy_or_gdal(dt) == 'gdal':
        
        dt = dt_converter(dt)
    if width == '':
        width = info['width'] - xoffset
    if height == '':
        height = info['height']- yoffset
    print
    print 'Reading raster:', Raster.split('/')[-1]
    print 'Band number:', band_no
    rast = gdal.Open(Raster)
    band1 = rast.GetRasterBand(band_no)
    print 'Datatype:',dt
    print width, height
    band1_pixels = band1.ReadAsArray(xoffset, yoffset, width, height).astype(dt)
    rast = None
    band1 = None
    print 'As datatype:',str(type(band1_pixels[1][1]))
    print
    return band1_pixels
    band1_pixels = None
def brick(Raster, dt = '', xoffset = 0, yoffset = 0, width = '', height = '', band_list = [], na_value = ''):
    info = raster_info(Raster)
    if band_list != []:
        bands = band_list
    else:
        bands = range(1, info['bands'] + 1)
    if dt == '':
        dt = info['dt']
    if numpy_or_gdal(dt) == 'gdal':
        
        dt = dt_converter(dt)
    if width == '':
        width = info['width'] - xoffset
    if height == '':
        height = info['height']- yoffset
    print
    print 'Reading raster:', Raster.split('/')[-1]
    print 'Datatype:',dt
    
    rast = gdal.Open(Raster)
    array_list = numpy.zeros([len(bands), height, width], dtype = dt)
    #array_list = []
    array_no = 0
    for band in bands:
        print 'Reading band number:', band
        band1 = rast.GetRasterBand(band)
        
        band1_pixels = band1.ReadAsArray(xoffset, yoffset, width, height).astype(dt)
        
        array_list[array_no] = band1_pixels
        array_no += 1
    rast = None
    band1 = None
    band1_pixels = None
    print 'Returning', len(array_list),'band 3-d array'
    #array_list = numpy.array(array_list)
    if na_value != '':
        array_list = numpy.ma.masked_equal(array_list, int(na_value))
    return array_list
    array_list = None
######################################################################################
def tile_array(array, tiles):
    out = numpy.hsplit(array, tiles)
    return out
def untile_array(tiled_array):
    out = numpy.hstack(tiled_array)
    return out
def image_tiler(image, tile_size_x = 1000, tile_size_y = 1000):
    info = raster_info(image)
    bands = info['bands']
    width = info['width']
    height = info['height']
    print width, height
    coords = info['coords']
    res = info['res']
    print coords
    ulx = coords[0]
    uly = coords[-1]
    tilesx = math.ceil(float(width)/ float(tile_size_x))
    tilesy = math.ceil(float(width)/float(tile_size_y))
    for tilex in range(tilesx):
        xmin = ulx + (tilex * tile_size_x* res) 
        xmax = ulx + (tilex * tile_size_x * res) + (tile_size_x * res)
        if xmax > coords[2]:
            xmax = coords[2]
        for tiley in range(tilesy):
            ymax = uly - (tiley * tile_size_y * res) 
            ymin = uly - (tiley * tile_size_y * res) - (tile_size_y * res)
            if ymin < coords[1]:
                ymin = coords[1]
            gdal_coords = str(xmin) + ' ' +str(ymin) + ' ' + str(xmax) + ' ' + str(ymax)
            #print gdal_coords
            output = os.path.splitext(image)[0] + '_Tile_' +str(tilex) + '_' + str(tiley) + '.img'
            if os.path.exists(output) == False:
                reproject(image, output, zone = info['zone'], datum = info['datum'], clip_extent = gdal_coords, resampling_method = 'nearest')
######################################################################################
########################################################################################
#Provides a quick mosaic method for on-the-fly tiled array writing to a larger raster
#Designed to avoid writing individual tiles, and then mosaicking them after all tiles are created
#The tiled_image object is really a gdal driver instance of the template image
#Individual sections of the driver can be written without bringing all tiles into memory at once
#Since a Numpy array is read in, all projection infomation must be provided within the template image
#The datatype (dt) can be overridden to a desired type regardless of the template's datatype
class tiled_image:
    def __init__(self, output, template_image = '', width = '', height = '', bands = '', dt = '', df = 'HFA'):
        t_info = raster_info(template_image)
        self.projection, self.transform = t_info['projection'], t_info['transform']
        if template_image != '':
            
            self.width, self.height = t_info['width'], t_info['height']
        if bands == '':
            self.bands = t_info['bands']
        else:
            self.bands = bands
        if dt == '':
            self.dt = t_info['dt']
            
        else:
            self.dt = dt
            
        if numpy_or_gdal(self.dt) == 'numpy':
        
            self.dt = dt_converter(self.dt)
        self.numpy_dt = dt_converter(self.dt)
        self.gdal_dt = 'gdal.GDT_' + self.dt
        print self.gdal_dt
        
        driver = gdal.GetDriverByName(df)
        print 'Initiating output raster:', output
        self.ds = driver.Create(output, self.width, self.height, self.bands, eval(self.gdal_dt))
        self.ds.SetProjection(self.projection)
        self.ds.SetGeoTransform(self.transform)

    def add_tile(self, array, x_offset, y_offset):
       
        if len(array) > self.bands:
            band_range = self.bands
        else:
            band_range = len(array)
        print 'Writing pixel values for offsets:', x_offset, y_offset  
        for band in range(band_range):
            band  += 1
            
            self.ds.GetRasterBand(band).WriteArray(array[band-1], x_offset, y_offset)
        array = None
    def rm(self):
        try:
            self.ds = None
        except:
            x = 'oops'
        
####################################################################################### 
#Will write a numpy array to a raster
#Byte, UInt16, Int16, UInt32, Int32, Float32, Float6
def write_raster(numpy_array,output_name, template = '', df = 'HFA', dt = 'Int16', width = '', height = '', bands = 1, projection = '', transform = ''):
    
    if numpy_or_gdal(dt) == 'numpy':
        
        dt = dt_converter(dt)

    dt = 'gdal.GDT_' + dt
    if template != '':
        rast = gdal.Open(template)
        width = rast.RasterXSize
        height = rast.RasterYSize
        #bands = rast.RasterCount
        projection = rast.GetProjection()

    if transform == '':
        transform = rast.GetGeoTransform()
    driver = gdal.GetDriverByName(df)
    ds = driver.Create(output_name, width, height, bands, eval(dt))
    ds.SetProjection(projection)
    ds.SetGeoTransform(transform)
    print 'Writing: ' + output_name.split('/')[-1]
    print 'Datatype of ' + output_name.split('/')[-1] + ' is: ' + dt
    if bands > 1:
        for band in range(1,bands + 1):
            ds.GetRasterBand(band).WriteArray(numpy_array[band-1])
    else:      
        ds.GetRasterBand(1).WriteArray(numpy_array)
    return output_name
    ds = None
    numpy_array = None
    rast = None
######################################################################################
#Stacks a list of rasters
#All rasters must be of the exact same extent
#Should use the 
def stack(image_list = [], output_name = '', template = '', df = 'HFA', dt = '', width = '', height = '', projection = '', transform = '', array_list = False, guiable = True):
    if image_list == []:
        image_list = str(askopenfilenames(title = 'Select Rasters to stack',filetypes=[("IMAGINE","*.img"),("tif","*.tif")])).split(' ')
        print image_list
    if output_name == '':
        output_name = str(asksaveasfilename(title = 'Select output image name',initialdir = cwd,filetypes=[("IMAGINE","*.img"),("tif","*.tif")])) 

    
   
    if dt == '' and array_list == False:
        info = raster_info(image_list[0])
        dt = info['dt']
    elif dt == '' and array_list == True:
        info = raster_info(template)
        dt = info['dt']
    if numpy_or_gdal(dt) == 'numpy':
        
        dt = dt_converter(dt)
    numpy_dt = dt_converter(dt)
    gdal_dt = 'gdal.GDT_' + dt
    print gdal_dt
    if template != '':
        rast = gdal.Open(template)
        width = rast.RasterXSize
        height = rast.RasterYSize
        projection = rast.GetProjection()
    elif width == '':
        info = raster_info(image_list[0])
        width = info['width']
        height = info['height']
        projection = info['projection']
        transform = info['transform']
    bands = len(image_list)
    if transform == '':
        transform = rast.GetGeoTransform()
    driver = gdal.GetDriverByName(df)
    print bands
    ds = driver.Create(output_name, width, height, bands, eval(gdal_dt))
    ds.SetProjection(projection)
    ds.SetGeoTransform(transform)
    print 'Writing: ' + output_name.split('/')[-1]
    print 'Datatype of ' + output_name.split('/')[-1] + ' is: ' + dt
    for band in range(bands):
        print 'Stacking band:', image_list[band]
        if array_list == False:
            array = raster(image_list[band], dt = numpy_dt)
        elif array_list == True:
            array = image_list[band]
        ds.GetRasterBand(band + 1).WriteArray(array)
    return output_name
    ds = None
    array = None
    rast = None

######################################################################################
#Restacks a specified list of bands from a stack into the specified order in the list
def restack(stack = '', output_name = '', template = '', band_list = [], df = 'HFA', dt = '', width = '', height = '', projection = '', transform = '', guiable = True):
    if stack == '':
        stack = str(askopenfilename(title = 'Select Stack to Rearrange',filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
       
    if output_name == '':
        output_name = str(asksaveasfilename(title = 'Select output image name',initialdir = cwd,filetypes=[("IMAGINE","*.img"),("tif","*.tif")])) 

    if band_list == []:
        temp = askstring('Bands to rearrange', 'Please enter band number in order to rearrange separated by commas (ex. 6,4,3)')
    
        temp = temp.split(',')
        sample_no_temp = []
        for sample in temp:
            index = 0
            sample_temp = ''
            for char in sample:
                if char != ' ':
                    sample_temp += char
            sample_no_temp.append(int(sample_temp))
        band_list = sample_no_temp
    
    info = raster_info(stack)
    if dt == '':
        
        dt = info['dt']
    if numpy_or_gdal(dt) == 'numpy':
        
        dt = dt_converter(dt)
    numpy_dt = dt_converter(dt)
    gdal_dt = 'gdal.GDT_' + dt
    print gdal_dt
    if template != '':
        rast = gdal.Open(template)
        width = rast.RasterXSize
        height = rast.RasterYSize
        projection = rast.GetProjection()

    else:
        width = info['width']
        height = info['height']
        projection = info['projection']
    bands = len(band_list)
    if transform == '':
        transform = info['transform']
        
    driver = gdal.GetDriverByName(df)
    
    
    
    ds = driver.Create(output_name, width, height, bands, eval(gdal_dt))
    ds.SetProjection(projection)
    ds.SetGeoTransform(transform)
    print 'Writing: ' + output_name.split('/')[-1]
    print 'Datatype of ' + output_name.split('/')[-1] + ' is: ' + dt
    for band in range(bands):
        print 'Stacking band:', band_list[band]
        array = raster(stack, band_no = band_list[band], dt = numpy_dt)
        ds.GetRasterBand(band + 1).WriteArray(array)
    
    ds = None
    array = None
    rast = None
    return output_name
######################################################################################
#Returns an array of zeros with the exact dimensions and datatype of the given template raster
#Datatype can be manually defined
#u1,u2,u4, i1,i2,i4, float32, float64
def empty_raster(Template_Raster, dt = ''):
    if dt == '':
        info = raster_info(Template_Raster)
        dt = info['dt']
    if numpy_or_gdal(dt) == 'gdal':
        
        dt = dt_converter(dt)
    
    print 'Creating empty raster from: ' + Template_Raster.split('/')[-1]
    rast = gdal.Open(Template_Raster)
    width = rast.RasterXSize
    height = rast.RasterYSize
    band1 = numpy.zeros([height, width]).astype(dt)
    print 'Datatype of empty raster is: ' + str(type(band1))
    rast = None
    return band1
    band1 = None
######################################################################################
def logit_apply(wd, predictors, coefficients, out_file):
    i = 0
    
    for predictor in predictors:
        r(predictor + '= ' + coefficients[i + 1] + '* raster("'+ wd + predictor + '")')
        i += 1
##        pred = gdal.Open(wd + predictor)
##        pred_pixels = pred.ReadAsArray()
##        print predictor, pred_pixels
##        pred = None
##        pred_pixels = None
######################################################################################
#Finds the intersection coordinates of a list of images
#All images must be the same projection
def intersection_coords(image_list):
    extent_list = []
    for pred in image_list:
        #print 'Processing: ' + pred
        rast = gdal.Open(pred)
        transform = rast.GetGeoTransform()
        ncol = rast.RasterXSize
        nrow = rast.RasterYSize
        xmin = transform[0]
        xmax = transform[0] + ncol * transform[1]
        ymax = transform[3]
        ymin = transform[3] - nrow * transform[1]
        extent_list.append([xmin,xmax,ymin,ymax])
    rast = None
    extent_list = numpy.array(extent_list)
    intersection = []
    for i in range(len(extent_list[0])):
        if (i + 2) %2 == 0:
            intersection.append(max(extent_list[:,i]))
        else:
            intersection.append(min(extent_list[:,i]))
    #print 'The intersection coords of', image_list, 'are', intersection
    return intersection
######################################################################################
#Will clip an image to the common extent of a list of images
#Can return an array of zeros of the common extent and/or can clip a single or multi-band image
#Returns a 3-d array.  If a single band raster is provided, the array is returned as the first within a list with length = 1
def clip(image = '', output_name = '', clip_extent_image_list = [], array_only = False, zeros_only = False, dt = '', guiable = True):
    if image == '':
        image = str(askopenfilename(title = 'Select image to clip',filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
        print image
    if output_name == '':
        output_name = str(asksaveasfilename(title = 'Select output image name',initialdir = cwd,filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
    if clip_extent_image_list == []:
        clip_extent_image_list = str(askopenfilenames(title = 'Select images to clip common extent to',filetypes=[("IMAGINE","*.img"),("tif","*.tif")])).split(' ')

    
    if dt == '':
        info = raster_info(image)
        dt = info['dt']
    coords = intersection_coords(clip_extent_image_list)
    rast = gdal.Open(image)
    transform = rast.GetGeoTransform()
    
    projection = rast.GetProjection()
    res_orig = transform[1]
    resolution = res_orig

    
    out_ncolumn = numpy.floor((coords[1]-coords[0])/resolution)
    out_nrow =  numpy.ceil((coords[3] - coords[2])/resolution)
    

    column_offset =  ((coords[0] - transform[0])/res_orig)#+1
   
    row_offset = ((transform[3]- coords[3] )/res_orig)#+1
    trans_list = [coords[0], transform[1], transform[2], coords[-1], transform[4], transform[5]]
    out_transform = tuple(trans_list)
    no_bands= rast.RasterCount
    rast = None
    array_list = None
    array_list = []
    for band in range(no_bands):
        
        array = raster(image, dt = dt, band_no = band + 1)

        print 'Clipping', image.split('/')[-1], 'band number ', band + 1, 'to', coords
        print 'Clip to:',out_nrow, out_ncolumn
        print 'Original:', numpy.shape(array)[0], numpy.shape(array)[1]
        #rast = gdal.Open(image)
        
        array = array[row_offset : (out_nrow + row_offset),column_offset: (out_ncolumn + column_offset)]
        print row_offset
        print column_offset
      
        

        if zeros_only == True:
            array = numpy.zeros([out_nrow, out_ncolumn]).astype(dt)
        array_list.append(array)
        
    if array_only == False:
        stack(array_list, output_name = output_name, width = int(out_ncolumn), height = int(out_nrow), projection = projection, transform = out_transform,dt = dt, array_list = True)
        #write_raster(array, output_name ,dt = dt,width = int(out_ncolumn), height = int(out_nrow), projection = projection, transform = out_transform)
    else:
        print 'Array_only is True'
        print 'Returned array with following dims:', numpy.shape(array)
    rast = None
    array = None
    return array_list
    
    array_list = None
######################################################################################
#Clips and snaps a list of rasters to the common extent of the rasters in the list
#All rasters must be the sampe projection and spatial resolution
#Rasters can be of different band numbers
def clip_list(input_list = [], output_suffix = '_clip.img', dt = '', overwrite = True, guiable = True):
    if input_list == []:
        input_list = str(askopenfilenames(title = 'Select images to clip to common extent',filetypes=[("IMAGINE","*.img"),("tif","*.tif")])).split(' ')


    out_list = []
    
    for Input in input_list:
        output = os.path.splitext(Input)[0] + output_suffix
        if os.path.exists(output) == False or overwrite == True:
            clip(Input, output, input_list, array_only = False, dt = dt)
        out_list.append(output)
        print
        print
    return out_list
######################################################################################
#Inverts the values of a thematic raster
def invert(Input = '' , Output = '', dt = '', guiable = True):
    if Input == '':
        Input = str(askopenfilename(title = 'Select image to invert values',filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
    if Output == '':
        Output = str(asksaveasfilename(title = 'Select output image name',initialdir = cwd,filetypes=[("IMAGINE","*.img"),("tif","*.tif")])) 

    
    

    
    if dt == '':
        info = raster_info(Input)
        dt = info['dt']
    if dt == 'Float32':
        dt = 'Int16'
    if numpy_or_gdal(dt) == 'gdal':
        
        numpy_dt = dt_converter(dt)
    else:
        numpy_dt = dt
  
    info = raster_info(Input)
    bands = info['bands']
    array_list= []
    for band in range(1,bands + 1, 1):
        in_rast = raster(Input, dt = dt, band_no = band)
    
        out_rast = numpy.invert(in_rast, dtype = numpy_dt)
        array_list.append(out_rast)
    stack(array_list, Output, Input, array_list = True)
    #write_raster(out_rast,Output, template = Input, dt = dt)
##    out_rast = empty_raster(Input, dt = dt)
##
##    Hist = hist([Input])[0]
##    print Hist
##    orig_values = []
##    new_values = []
##    i = 1
##    for Bin in Hist[1:]:
##        if Bin > 0:
##            orig_values.append(i)
##            new_values.append(i)
##        i +=1
##   
##    new_values.reverse()
##    print len(orig_values), len(new_values)
##    print 'Converting the following values:'
##    for i in range(len(orig_values)):
##        print orig_values[i], '=', new_values[i]
##        out_rast[in_rast == orig_values[i]] = new_values[i]
##        
##       
##    print
##    print
    in_rast = None
##    write_raster(out_rast,Output, template = Input, dt = dt)
    out_rast = None

######################################################################################
#Recodes a raster based on provided bin breaks
#Recode values are incremented by 1 starting with 1
#Ex recode_list = [1,10,20]... 1 = 1, 2-10 = 2, 11-20 = 3
def recode(Input = '', Output = '', recode_list = [], dt = '', guiable = True):
    if Input == '':
        Input = str(askopenfilename(title = 'Select image to recode',filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
    if Output == '':
        Output = str(asksaveasfilename(title = 'Select output image name',initialdir = cwd,filetypes=[("IMAGINE","*.img"),("tif","*.tif")])) 

    
    if recode_list == []:
        temp = askstring('Recode values', 'Please enter recode value list\n(ex: 1, 10, 20, 30 would result in 1 = 1, 2-10 = 2, 11-20 = 3, 21-30 = 4)')
    
        temp = temp.split(',')
        sample_no_temp = []
        for sample in temp:
            index = 0
            sample_temp = ''
            for char in sample:
                if char != ' ':
                    sample_temp += char
            sample_no_temp.append(int(sample_temp))
        recode_list = sample_no_temp
    


    if dt == '':
        info = raster_info(Input)
        dt = info['dt']
    array = raster(Input, dt = dt)
    base = empty_raster(Input, dt)
    base[base == 0] += 1
    for i in range(1, len(recode_list)-1):
        print recode_list[i]
        base[array > recode_list[i]] += 1
        i += 1
    base[array == 0] = 0
    write_raster(base,Output, template = Input, dt = dt)
    array = None
######################################################################################
def make_mask(Input, Output, gt_value = 0, mask_value = 1, dt = 'Byte'):
    info = raster_info(Input)
    input_dt = info['dt']
    array = raster(Input, dt = input_dt)
    base = empty_raster(Input, dt)
    base[array > gt_value] = mask_value
    write_raster(base, Output, template = Input, dt = dt)
######################################################################################
#fun_options = numpy.mean, numpy.max, numpy.min, numpy.std, numpy.var, numpy.median, 
#adjacency_options = 4, 8
def middle(List):
    half = int(numpy.floor(len(List)/2))
    return half
def focal_filter(Input, Output = '', fun = 'mean', matrix = 'low_pass', kernel_size = 3, return_array = True):
    start = time.time()
    
    matrix_dict = {'high_pass': [1.0,-9.0], 'low_pass': [1.0,1.0], 'edge_detect':[8.0, -1.0], 'edge_enhance' : [17.0, -1.0]}
    kernel_size = int(kernel_size)
    while int(kernel_size)%2 == 0:
        print 'kernel_size must be an odd number'
        kernel_size = int(raw_input('Please re-enter the kernel size: '))
    if type(matrix) == str:
        matrix_type = string.lower(matrix)
        matrix = []
        numbers = matrix_dict[matrix_type]
        mid = middle(range(kernel_size))
        for i1 in range(kernel_size):
            temp = []
            for i2 in range(kernel_size):
                if i1 == mid and i2  == mid:
                    temp.append(numbers[1])
                else:
                    temp.append(numbers[0])
            matrix.append(temp)
                     
    if type(matrix) != list:
        print 'Must enter a matrix type or a matrix'
        raw_input('Press enter to exit')
        sys.exit()
      
    info = raster_info(Input)
    dt = info['dt']
    bands = info['bands']
    band_list = []
    for band in range(1,bands +1):
        print 'Finding focal', fun, 'for band', band
        try:
            array = raster(Input, band_no = band, dt = dt)
            out = empty_raster(Input, dt = dt)
            
            nd_image.generic_filter(array, eval(fun), footprint = matrix, output = out)
        except:
            array = None
            out = None
            array = raster(Input, band_no = band, dt = dt)
            out = empty_raster(Input, dt = dt)
            nd_image.generic_filter(array, eval('numpy.' + fun), footprint = matrix, output = out)
        band_list.append(out)
        
    #write_raster(out, Output, Input, dt = dt)
    if Output != '':
        stack(band_list, Output, template = Input, dt = dt, array_list = True)
    array = None
    out = None
    
    end = time.time()
    print 'Took:', end - start,'seconds to complete'
    if return_array == True:
        return band_list
    band_list = None
    
#Input = 'O:/02_Inputs/Aster/Baltimore/Inputs/Landsat_Spectral/015033_03320060824L5_toa_summer_proj_clip.img'
#Output = os.path.splitext(Input)[0] + 'stack_test5.img'

#focal_filter(Input, Output, 'mean', 'high_pass',kernel_size = 3)

######################################################################################
#Creates individual binary 1/0 masks for a given strata raster
#The strata raster should have integer valuse
#Each strata value will be broken into an individual raster with the value it came from in the name
def break_strata(strata_raster = '', out_dir = '', dt = '', exclude_list = [],overwrite = False, guiable = True):
    if strata_raster == '':
        strata_raster = str(askopenfilename(title = 'Select thematic strata image to break',filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
    if out_dir == '':
        askdirectory(initialdir = cwd, title = 'Please select an output directory')
    
    if dt == '':
        info = raster_info(strata_raster)
        dt = info['dt']
    array = raster(strata_raster, dt = dt)
    strata = range(numpy.amin(array), numpy.amax(array) + 1, 1)
    out_list = []
    for num in strata:
        if num not in exclude_list:
            name = out_dir + os.path.splitext(strata_raster.split('/')[-1])[0] + '_' + str(num) + '.img'
            if os.path.exists(name) == False or overwrite == True:
                temp = empty_raster(strata_raster, dt = dt)
                temp[array == num] = 1
                write_raster(temp, name, strata_raster, dt = dt)
                temp = None
            out_list.append(name)
    return out_list
    array = None
######################################################################################
#Combines a list of images from a list of masks (likely produced from the "break_strata" function
#All images must be the exact same extent/projection
#Creates a single raster mosaic based on the masks
#mask_image_list must be a 2-d array with the syntax as follows:
#mask_image_list = [[mask, image],[mask,image].....]
def combine_strata(mask_image_list = [], output = '', dt = '', mask_no = 1, overwrite = True, guiable = True):
    if mask_image_list == []:
        temp1 = str(askopenfilenames(title = 'Select mask rasters (remember order)',filetypes=[("IMAGINE","*.img"),("tif","*.tif")])).split(' ')
        temp2 = str(askopenfilenames(title = 'Select continuous rasters based on the masks in same order',filetypes=[("IMAGINE","*.img"),("tif","*.tif")])).split(' ')
        mask_image_list = []
        if len(temp1) != len(temp2):
            print 'Must select the same number of mask and continuous images'
            pass
        for i in range(len(temp1)):
            mask_image_list.append([temp1[i], temp2[i]])
    if output == '':
        output = str(asksaveasfilename(title = 'Select output image name',initialdir = cwd,filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
        
    if dt == '':
        info = raster_info(mask_image_list[0][1])
        dt = info['dt']
    base = empty_raster(mask_image_list[0][0], dt = dt)
    print base
    for strata in mask_image_list:
        print strata
        mask_raster = strata[0]
        strata_raster = strata[1]
        if os.path.exists(mask_raster) and os.path.exists(strata_raster):
            mask_array = raster(mask_raster, dt = dt)
            strata_array = raster(strata_raster, dt = dt)
            base += mask_array * strata_array
    write_raster(base, output, mask_image_list[0][0], dt = dt)
    base = None
    mask_array = None
    strata_array = None
######################################################################################
#Will increment the image value by the mask value
#Works with single band images currently
def increment_by_mask(image = '', mask = '', output = '', dt = '', mask_no = 1, overwrite = True, guiable = True):
    img =  raster(image)
    msk = raster(mask)
    array = img + msk
    
    stack([array], output, mask, array_list = True)
    img = None
    msk = None
    array = None
    
#Will mask out a raster based on a provided mask
#The mask value can be defined- default = 1
#The image can be a raster or a numpy array
#If a numpy array is provided, but no datatype is explicitly defined, the datatype of the mask is used (likely should define datatype)
def mask(image = '', mask = '', output = '', dt = '', mask_no = 1, overwrite = True, guiable = True):
    if image == '':
        image = str(askopenfilename(title = 'Select image to mask',filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
    if mask == '':
        mask = str(askopenfilename(title = 'Select mask image (default mask value = 1)',filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
    if  output == '':
        output = str(asksaveasfilename(title = 'Select output image name',initialdir = cwd,filetypes=[("IMAGINE","*.img"),("tif","*.tif")])) 

    

    try:
        info = raster_info(image)
        bands = info['bands']
    except:
        x = 'oops'
        bands = 1
    if dt == '':
        try:
            
            dt = info['dt']
        except:
            info = raster_info(mask)
            dt = info['dt']
        info_m = raster_info(mask)
        dt_m = info_m['dt']
    else:
        dt = dt
        dt_m = dt
    mask_temp = mask
    array_list = []
    if os.path.exists(output) == False or overwrite == True:
        for band in range(1, bands + 1, 1):
            try:
                array = raster(image, dt = dt, band_no = band)
            
            except:
                array = image
            try:
                mask = raster(mask, dt = dt_m)
            except:
                mask = mask
            array[mask < mask_no] = 0
            array_list.append(array)
        #write_raster(array, output, mask_temp, dt = dt)
        stack(array_list, output, mask_temp, dt = dt, array_list = True)
    array = None
    mask = None
    array_list = None
######################################################################################
#Finds the common area with values greater than or equal to the lt_no of a list of rasters
#All rasters provided must be the exact same extent (can use the "clip_list" function)
#Each raster is masked wherever there are values within the list of rasters that are less than the lt_no
def stack_clip(input_list = [], output_dir = '', output_suffix = '_intersection.img', dt = '', lt_no = 1, overwrite = True, guiable = True):
    if input_list == []:
        input_list = str(askopenfilenames(title = 'Select images to find common data extent\nMust be the same extent\nUse Clip_list to ensure the images are the same extent',filetypes=[("IMAGINE","*.img"),("tif","*.tif")])).split(' ')
    if output_dir == '':
        output_dir = str(askdirectory(initialdir = cwd, title = 'Please select an output directory')) + '/'
    


    
    if dt == '':
        info = raster_info(input_list[0])
        dt = info['dt']
    out_list = []
    base = raster(input_list[0], dt = dt)
    output = output_dir + os.path.splitext(input_list[0])[0].split('/')[-1] + output_suffix
    if os.path.exists(output) == False or overwrite == True:
        
        print base
      
        for Input in input_list:
            output = output_dir + os.path.splitext(Input)[0].split('/')[-1] + output_suffix
            if os.path.exists(output) == False or overwrite == True:
                rast = gdal.Open(Input)
                no_bands= rast.RasterCount
                rast = None
                print overwrite
                print 'Compiling intersection of:' , Input.split('/')[-1]
                for band in range(no_bands):
                
                    array = raster(Input, band_no = band + 1, dt = dt)
                    print
                
                    base[array < lt_no] = 0
                    array = None
        
        base[base > 0] = 1
    
    intersection_list = []
    
    
    for Input in input_list:
        rast = gdal.Open(Input)
        no_bands= rast.RasterCount
        rast = None
        array_list = []
        print 'Processing:',Input.split('/')[-1]
        output = str(output_dir + os.path.splitext(Input)[0].split('/')[-1] + output_suffix)
        if os.path.exists(output) == False or overwrite == True:
            for band in range(no_bands):
                
                
                array = raster(Input, band_no = band + 1, dt = dt)
                
                array[base == 0] = 0
                array_list.append(array)
                array = None
            #print input_list[0]
            print 'output',type(output)
            info = raster_info(input_list[0])
            print info['height'], info['transform']
            
            stack(array_list, output_name = output,height = info['height'],width = info['width'], projection = info['projection'], transform = info['transform'], dt = dt, array_list = True)
            array_list = None
            #write_raster(array, output, input_list[1], dt = dt)
            print
            print
        intersection_list.append(output)
    return intersection_list
    base = None
    array = None
######################################################################################
def stack_mask(input_list, output, dt = '', lt_no = 1):
    if dt == '':
        info = raster_info(input_list[0])
        dt = info['dt']
    out_list = []
    base = raster(input_list[0])
    for Input in input_list[1:]:
        print 'Compiling intersection of:' , Input.split('/')[-1]
        print 'Lt_no = ' , lt_no
        array = raster(Input)
        base[array < lt_no] = 0
        
    base[base > 0] = 1
    write_raster(base, output, input_list[1],dt = dt)
    base = None
    array = None
######################################################################################
def variety(input_list, output = '', dt = 'Int16', hist_only = False):
    if len(input_list) < 2:
        print 'Must have more than one raster to compute variety from'
        raw_input('Press enter to exit')
        sys.exit()
        
    base = raster(input_list[0])
    var = empty_raster(input_list[0])
    var[base > 0] = 1
    for Input in input_list[1:]:
        array = raster(Input)
        var[base != array] = len(input_list)
        #return numpy.select([base != array],[var + 1])
    bins = range(0, len(input_list) + 1)
    
    
    print list(numpy.histogram(var,bins)[0])
    if hist_only == False:
        write_raster(var, output, input_list[1], dt = dt)
    return list(numpy.histogram(var,bins)[0])
######################################################################################
#Computes the pixel count of a list of integer rasters
#By default, a count is computed for each value.  Bins can be provided as a list
def hist(image_list = [], table_name = '', bins ='', dt = '', band_no = 1, guiable = True):
    if image_list == []:
        
        image_list = str(askopenfilenames(title = 'Select image(s) to compute the pixel count for',filetypes=[("IMAGINE","*.img"),("tif","*.tif")])).split(' ')
        table_name = str(asksaveasfilename(title = 'Select the output table name',initialdir = cwd,filetypes=[("TAB","*.txt"),("txt","*.txt")])) 
   


    
    if dt == '':
        info = raster_info(image_list[0])
        dt = info['dt']
    hist_list = ''
    out_list = []
    for image in image_list:
        print 'Computing pixel count for:',image
        array = raster(image, dt = dt, band_no = band_no)
        if bins == '':
            bins = range(numpy.amin(array), numpy.amax(array) + 2, 1) 
        temp = list(numpy.histogram(array, bins)[0])
        line = image.split('/')[-1] + '\t'
        int_list = []

        for num in temp:
            line += str(num) + '\t'
            int_list.append(int(num))
        line = line[:-1] + '\n'
        hist_list += line
        out_list.append(int_list)
    hist_list = str(hist_list)
    columns = range(0,len(hist_list.split('\n')[0].split('\t')) -1, 1)
    header = 'Image_Name'
    for column in columns:
        header += '\t' + str(column)
    header += '\n'
    hist_list = header + hist_list
    if table_name != '':
        open_hist = open(table_name, 'w')
        open_hist.writelines(hist_list)
        open_hist.close()
    return out_list
######################################################################################
#Unstacks a stacked raster
#Can specify which layers should be unstacked (ex: layers = [4,5,6] will only unstack layers 4, 5, and 6)
def unstack(stack = '', dt = '', layers = 'All', overwrite = False, guiable = True):
    if stack == '':
        stack = str(askopenfilename(title = 'Select image to unstack',filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
    if dt == '':
        info = raster_info(stack)
        dt = info['dt']
    rast = gdal.Open(stack)
    
    if layers == 'All':
        n = rast.RasterCount
        layers = range(1,n+1)
    layer_list = []
    for i in layers:
        out_name = os.path.splitext(stack)[0] + '_' + str(i) + '.img'
        if os.path.exists(out_name) == False or overwrite == True:
            array = raster(stack, band_no = i, dt = dt)
        
            write_raster(array, out_name, stack, dt = dt, bands = 1)
        layer_list.append(out_name)
    array = None
    rast = None
    return layer_list
######################################################################################
#Gets the gdal coords of a raster for use in gdalwarp.exe
def get_gdal_coords(extent_raster):
    rast = gdal.Open(extent_raster)
    transform = rast.GetGeoTransform()
    width = rast.RasterXSize
    height = rast.RasterYSize
    transform = list(transform)
    rast = None
    xmax = transform[0] + (int(transform[1]) * width)
    xmin = transform[0]
    ymax = transform[3] 
    ymin = transform[3]- (int(transform[1]) * height)
      
    coords = str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax)
    return coords

########################################################################################################################
format_dict =  {'.tif': 'GTiff', '.img' : 'HFA', '.jpg' : 'JPEG', '.gif' : 'GIF', '.grid' : 'AAIGrid', '.hdr': 'envi'}
#Converts the format of a raster using the gdal_translate.exe
#Use 'HFA' for .img
def convert(Input = '', Output = '', Format = 'GTiff', gdal_dir = program_files_dir + '/FWTools2.4.7/bin/', guiable = True):
   
    if Input == '':
        Input = str(askopenfilename(title = 'Select image to convert',filetypes=[("IMAGINE","*.img"),("tif","*.tif"),("ENVI","*.hdr")]))
        Output = str(asksaveasfilename(title = 'Select output image name with format extension',initialdir = cwd,filetypes=[("IMAGINE","*.img"),("tif","*.tif"),("ENVI","*.hdr")])) 

        extension = os.path.splitext(Output)[1]
        Format = format_dict[extension]

        if os.path.splitext(Input)[1] == '.hdr':
            Input = os.path.splitext(Input)[0]
        if os.path.splitext(Output)[1] == '.hdr':
            Output = os.path.splitext(Output)[0]
            
    
    gdal_call = gdal_dir + 'gdal_translate -of ' + Format + ' ' + Input + ' ' + Output
    print gdal_call
    call = subprocess.Popen(gdal_call)
    call.wait()
########################################################################################################################
def batch_convert(in_folder, out_folder, convert_from_extension = '.hdr', out_format = 'GTiff', overwrite = False):
    extension_dict = {'HFA' : '.img', 'GTiff' : '.tif', 'ENVI' : '', 'AAIGrid' : '.grid'}
    if os.path.exists(out_folder) == False:
        os.makedirs(out_folder)
    images = filter(lambda i: os.path.splitext(i)[1] == convert_from_extension, os.listdir(in_folder))
    images = map(lambda i : in_folder + i, images)
    for image in images:
        if convert_from_extension == '.hdr':
            image = os.path.splitext(image)[0]
        output = out_folder + os.path.basename(os.path.splitext(image)[0]) + extension_dict[out_format]
        if os.path.exists(output) == False or overwrite == True:
            convert(image, output, Format = out_format)
        else:
            print os.path.basename(output), 'already exists'
########################################################################################################################
def make_vct_header(image, header_offset = '0', file_type = 'ENVI Standard', dt_dict = {'Byte': '1', 'UInt16': '12','Int16': '12'}, interleave = 'bsq', byte_order = '0', proj = 'UTM'):
    datum_dict = {'WGS84' : 'WGS-84', 'NAD83' : 'NAD-83'}
    info = raster_info(image)
    hl = ['ENVI\n', 'description = {\n', image + '}\n']
    samples = str(info['width'])
    lines = str(info['height'])
    bands = str(info['band_count'])
    dt = str(dt_dict[info['dt']])
   
    hl.append('samples = ' + samples + '\n')
    hl.append('lines = ' + lines + '\n')
    hl.append('bands = ' + bands + '\n')
    hl.append('header offset = ' + header_offset + '\n')
    hl.append('file type = ' + file_type + '\n')
    hl.append('data type = ' + dt + '\n')
    hl.append('interleave = ' + interleave + '\n')
    hl.append('byte order = ' + byte_order + '\n')
    
    coord1 = str(info['coords'][0])
    coord2 = str(info['coords'][-1])
    res = str(int(info['res']))
    zone = str(int(info['zone']))
    hemisphere = info['hemisphere']
    datum = datum_dict[info['datum']]
    units = info['units']
    map_info = 'map info = {' + proj + ', 1, 1, ' + coord1 + ', ' + coord2 + ', ' + res + ', ' + res + ', ' + zone + ', ' + hemisphere + ', ' + datum + ', units=' + units + '}\n'
    hl.append(map_info)
    hl.append('band names = {\n')
    band_count = info['band_count']
    for band in range(band_count):
        band = str(band + 1)
        hl.append('Band ' + band + ', ')
    hl[-1] = hl[-1][:-2] + '}\n'

    
    header = os.path.splitext(image)[0] + '.hdr'
    print 'Writing header:', header
    open_file = open(header, 'w')
    open_file.writelines(hl)
    open_file.close()
########################################################################################################################
#Will reproject a shapefile using ogr2ogr
#Can specify the crs manually as a string, only define the necessary parts of a UTM coordinate system, or define the proj = 'Albers' for albers
def reproject_shapefile(shapefile = '', output = '', crs = '', proj = 'utm', zone = '', datum = 'nad83', gdal_dir = gdal_dir, guiable = True):
    if shapefile == '':
        shapefile = str(askopenfilename(title = 'Select shapefile to reproject',filetypes=[("Shapefile","*.shp")]))
        output = str(asksaveasfilename(title = 'Select output shapefile name',initialdir = cwd,filetypes=[("Shapefile","*.shp")])) 
        proj = askstring('Projection', 'Please enter projection name (e.g. utm, or albers)')
        #if proj != 'albers' or proj == 'Albers' or proj == 'albers_conical'

    if proj == 'albers' or proj == 'Albers' or proj == 'albers_conical':
        #Use for USA Contiguous Albers Equal Area Conic USGS.prj
        #Same as in MTBS .prj file:
        #PROJCS["USA_Contiguous_Albers_Equal_Area_Conic_USGS_version",GEOGCS["GCS_North_American_1983",
        #DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],
        #UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],
        #PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-96.0],PARAMETER["Standard_Parallel_1",29.5],
        #PARAMETER["Standard_Parallel_2",45.5],PARAMETER["Latitude_Of_Origin",23.0],UNIT["Meter",1.0]]
        crs = '"+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs +towgs84=0,0,0"'
    elif crs == '':
        crs = '"+proj=' + proj + ' +zone=' + zone + ' +datum=' + datum + '"'
    

    statement = gdal_dir + 'ogr2ogr -f "ESRI Shapefile" -t_srs ' + crs + ' ' + output + ' ' + shapefile
    print statement
    call = subprocess.Popen(statement)
    call.wait()
#####################################################################################################
def utm_maker(shapefile, output, zone, datum):
    temp_folder = os.path.dirname(output) + '/temp/'
    if os.path.exists(temp_folder) == False:
        os.makedirs(temp_folder)
   
        
    proj_shp = temp_folder + os.path.basename(os.path.splitext(shapefile)[0]) + '_zone_' + str(zone) + '.shp'
    if os.path.exists(proj_shp) == False:
        reproject_shapefile(shapefile, proj_shp, zone = zone, datum = datum)

    proj_info = shape_info(proj_shp, False)
    shp_info = shape_info(shapefile, False)
    pc = proj_info['coords']
    sc = shp_info['coords']
    return proj_shp, sc, pc
########################################################################################################################
def xy_utm_zone_conversion(shapefile, zone, extension = '_convert', datum = 'WGS84', cleanup = False):
    zone = str(zone)
    output = os.path.splitext(shapefile)[0] + '_zone_' + zone + extension + '.shp'
    if os.path.exists(output) == False:
        reproject_shapefile(shapefile, output, datum = 'WGS84', zone = str(zone))
    out = xy_coords(output, False)
    if cleanup == True:
        try:
            delete_shapefile(output)
        except:
            print 'Could not delete', output
    return out   
########################################################################################################################
#Reprojects a raster using gdalwarp
#Will produce lines with zero values if RMSE is high
#Can specify the crs manually as a string, only define the necessary parts of a UTM coordinate system, or define the proj = 'Albers' for albers
#resampling_method:  near (default), bilinear, cubic, cubicspline, lanczos
#clip_extent: 'xmin ymin xmax ymax'
def reproject(Input, output, crs = '', proj = 'utm', zone = '', datum = 'nad83' , res = '',resampling_method = 'cubic', clip_extent = '', no_data = '', Format = 'HFA', dt = '', gdal_dir = gdal_dir):
    if type(Input) == list:
        temp = Input
        Input = ''
        for t in temp:
            Input += t + ' '
        Input = Input[:-1]
    if crs == '':
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
            crs = '"+proj=' + proj + ' +zone=' + str(zone) + ' +datum=' + str(datum) + '"'
    elif crs[0] != '"':
        crs = '"' + crs + '"'
    if crs != '':
        crs = ' -t_srs ' + crs
    
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
def batch_reproject(image_list, out_folder, suffix = '_proj.img', clip_extent = '', res = '', crs = '', datum = '', zone = '', resampling_method = 'cubic'):
    out_list = []
    for image in image_list:
        output = out_folder + os.path.basename(os.path.splitext(image)[0])+ suffix
        if os.path.exists(output) == False:
            reproject(image, output, zone = zone, datum = datum, crs = crs, res = res, resampling_method = resampling_method, clip_extent = clip_extent)
        out_list.append(output)
    return out_list
########################################################################################################################
#Will select a shapefile feature by attribute and create a new shapefile
#Uses common sql syntax, but is slightly simplified
#Ex: To select all features with a field named "Population" that has a value greater than 1000 the syntax would be:
# sql_statement = 'Population > 1000'
def select_by_attribute(shapefile, output, sql_statement, gdal_dir = gdal_dir):
    statement = gdal_dir + 'ogr2ogr -f "ESRI Shapefile" -sql "SELECT * FROM ' + os.path.splitext(shapefile.split('/')[-1])[0] + ' WHERE ' + sql_statement + '" ' + output + ' ' + shapefile
    print
    print
    print 'Selecting using following string:'
    print statement
    call = subprocess.Popen(statement)
    call.wait()
########################################################################################################################
#Copies a shapefile
#Providing a .shp extension is optional
def copy_shapefile(source, destin, extension_list = ['.shx', '.dbf', '.prj', '.sbn', '.sbx', '.shp', '.shp.xml']):
    source = os.path.splitext(source)[0]
    destin = os.path.splitext(destin)[0]
    for extension in extension_list:
        File = source + extension
        out = destin + extension
        if os.path.exists(File) == True:
            shutil.copy(File, out)
########################################################################################################################
#Deletes a shapefile
#Providing a .shp extension is optional
def delete_shapefile(source, extension_list = ['.shx', '.dbf', '.prj', '.sbn', '.sbx', '.shp', '.shp.xml']):
    source = os.path.splitext(source)[0]
    
    for extension in extension_list:
        File = source + extension
        
        if os.path.exists(File) == True:
            os.remove(File)
########################################################################################################################
#Clips a shapefile to the extent of a raster using the ogr2ogr.exe
#Must be of the same projection (ogr2ogr does not support on-the-fly reprojection)
def clip_shapefile(shapefile, extent_raster = '', extent_coords = '', output = '', gdal_dir = gdal_dir):
    if extent_raster != '':
        coords = get_gdal_coords(extent_raster)
    else:
        coords = extent_coords
    print coords
    statement = gdal_dir + 'ogr2ogr -f "ESRI Shapefile" -clipsrc ' + coords + ' ' + output + ' ' + shapefile
    print statement
    call = subprocess.Popen(statement)
    call.wait()
########################################################################################################################
#Calculates the x, y coordinates of a point shapefile using the r library "maptools"
#Returns a 2-d array of the coordinates
#There is the option of producing a csv file with the coordinates as well
def xy_coords(shapefile, write_csv = True, csv_name = ''):
    try:
        r('library(maptools)')
    except:
        r_library_installer(['maptools'])
        r('library(maptools)')
        
    r('pt = readShapePoints("' + shapefile + '")')
    x_coords = r('x_coords = (coordinates(pt)[,1])')
    y_coords = r('y_coords = (coordinates(pt)[,2])')
    out_list = []
    csv_lines = 'x,y\n'
    for i in range(len(x_coords)):
        out_list.append([x_coords[i], y_coords[i]])
        csv_lines += str(x_coords[i]) + ',' + str(y_coords[i]) + '\n'
    if write_csv == True:
        csv_open = open(csv_name, 'w')
        csv_open.writelines(csv_lines)
        csv_open.close()
    return out_list
########################################################################################################################
#Converts a raster to a shapefile using the FWTools gdal_polygonize.py script
def raster_to_shapefile(raster, output, overwrite = False, gdal_dir = gdal_dir):
    statement = 'gdal_polygonize.py ' + raster + ' -f "ESRI Shapefile" ' + output + ' ' + os.path.splitext(os.path.basename(output))[0]
    
    orig_dir =  os.getcwd()
    os.chdir(gdal_dir)
  
    
    bat_filename = os.path.dirname(raster) + '/gdal_polygonize.bat'
    open_bat = open(bat_filename, 'w')
    open_bat.writelines(statement)
    open_bat.close()
    if os.path.exists(output) == False or overwrite == True:
        call = subprocess.Popen(bat_filename)
        call.wait()
    os.chdir(orig_dir)
    try:
        os.remove(bat_filename)
    except:
        x = 1
########################################################################################################################
#Converts a shapefile to a raster using the r package "raster" polygonize function
#Can provide an optional snap raster if available- otherwise conversion is performed with raster snapped to nearest coordinate from ulx,uly
def shapefile_to_raster(shapefile, output, snap_raster = '', resolution = '10'):
    start = time.time()
    resolution = str(resolution)
    try:
        r('library(raster)')
    except:
        r_library_installer(['raster'])
        r('library(raster)')
    if snap_raster == '':
        layer = os.path.splitext(shapefile)[0].split('/')[-1]
        try:
            r('library(raster)')
        except:
            r_library_installer(['raster'])
            r('library(raster)')
        try:
            r('library(rgdal)')
        except:
            r_library_installer(['rgdal'])
            r('library(rgdal)')
       
        r('shp = readOGR("' + shapefile + '", "' + layer + '")')
        r('projection = OGRSpatialRef("' + shapefile + '", "' + layer + '")')
        r('info = ogrInfo("' + shapefile + '", "' + layer + '")')
        r('extent =as.matrix((bbox(shp)))')
        r('print(extent[1,])')

        r('xmaxmin = extent[1,]')
        
        r('ymaxmin = extent[2,]')
        r('ncol = as.numeric((xmaxmin[2] - xmaxmin[1])/' + resolution + ')')
        r('nrow = as.numeric((ymaxmin[2] - ymaxmin[1])/' + resolution + ')')
        r('ncol = ceiling(ncol)')
        r('nrow = ceiling(nrow)')
        r('print(ncol)')
        r('print(nrow)')
        r('dtype = "INT1U"')

        r('extent[1,2] = extent[1,1] + (ncol * ' + resolution + ')')
        r('extent[2,2] = extent[2,1] + (nrow * ' + resolution + ')')

        r('resolution = '+resolution)
    else:
        try:
            r('temp = raster("' + snap_raster + '")')
        except:
            r('library(raster)')
            r('temp = raster("' + snap_raster + '")')
        

        r('projection = projection(temp)')
        r('extent = extent(temp)')
        r('ncol = ncol(temp)')
        r('nrow = nrow(temp)')
        r('dtype = dataType(temp)')
        
    r('r = raster(ncol = ncol, nrow = nrow)')
    r('projection(r) = projection')
    r('extent(r) = extent')
  
    r('r[] = 0')
    r('print(r)')
    try:
        r('poly = readShapePoly("'+shapefile+'", proj4string = CRS(projection(r)), delete_null_obj = TRUE)')
    except:
        try:
            r('library(maptools)')
        except:
            r_library_installer(['maptools'])
            r('library(maptools)')
        
        r('poly = readShapePoly("'+shapefile+'", proj4string = CRS(projection(r)), delete_null_obj = TRUE)')
    r('r = rasterize(poly, r, progress = "text", na.rm = TRUE, update = TRUE)')
    
    
    r('writeRaster(r, "'+output+'", datatype = dtype, format = "HFA", overwrite = TRUE)')
    end = time.time()
    elapsed_time = end - start
    print "Took: ", elapsed_time, "seconds to complete"
##############################################################################################
#Will merge a list of shapefiles to a single shapefile using ogr2ogr.exe
#All shapefiles must be of the same type (point, polyline, or polygon), and projection (ogr2ogr does not support on-the-fly reprojection)
def merge_shapefile(merge_list, output_name, gdal_dir = gdal_dir):
    if os.path.exists(merge_list[0]) == True:
        if os.path.exists(output_name) == False:
            try:
                make_merge_shp = gdal_dir + 'ogr2ogr -f "ESRI Shapefile" ' + output_name + ' ' + merge_list[0]
                print make_merge_shp
                call = subprocess.Popen(make_merge_shp)
                call.wait()
            except:
                'Could not create', output_name
    else:
        print merge_list[0], 'does not exist'
    for merge in merge_list[1:]:
        merge_call = gdal_dir + 'ogr2ogr -f "ESRI Shapefile" -update -append ' + output_name + ' ' + merge + ' -nln ' + os.path.basename(os.path.splitext(output_name)[0])
        print 'Merging:', os.path.basename(merge)
        call = subprocess.Popen(merge_call)
        call.wait()
##############################################################################################
#Will clip a shpefile to the extent or a raster and then convert the shapefile to a raster
#Uses the extent raster for the geographic extent and as a snap raster
#Projection of the shapefile and extent_raster must be the same
def clip_shapefile_to_raster(shapefile, extent_raster, output):
    temp = os.path.splitext(output)[0] + '_temp_clip.shp'
    clip_shapefile(shapefile, extent_raster, temp)
    shapefile_to_raster(temp, extent_raster, output)
######################################################################################
#Adds a field to a shapefile using ogr
#User can define the field type with the following options:
#Datatypes: Integer, Real, String, Float
def add_field(shapefile, field_name, datatype = 'Integer'):
    source = ogr.Open(shapefile, 1)
    layer = source.GetLayer()
    layer_defn = layer.GetLayerDefn()
    field_names = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]
    print 'Currently existing field names are:', field_names
    if field_name not in field_names:
        print 'Adding field name: ', field_name
        new_field = ogr.FieldDefn(field_name, eval('ogr.OFT' + datatype))
        layer.CreateField(new_field)
    else:
        print field_name, 'already exists'
    source.Destroy()
########################################################################################################################
#Updates a field within a shapefile with a provided list of values
#The list of values must be of the same type as the field (list of strings for a string field type....)
#The list of values must have the same number of entries as there are features within the shapefile
def update_field(shapefile, field_name, value_list):
    dbf_file = os.path.splitext(shapefile)[0] + '.dbf'
    db1 = dbf.Dbf(dbf_file, readOnly = False, ignoreErrors = True)
    if len(db1) != len(value_list):
        print 'Shapefile record number('+str(len(db1))+') is different from provided value list('+str(len(value_list))+')'
        print 'Cannot update field:', field_name
        
    else:
        print 'Updating values for field:', field_name
        for row in range(len(db1)):
            rec = db1[row]
            rec[field_name] = value_list[row]
            rec.store()
    db1.close()
########################################################################################################################
#Uses the epv function in the rRsac_Tools.r library to extract the point values from a raster
#Uses the r libraries raster and maptools
#Returns a list of values
def extract_value_to_list(shapefile, raster, rscript = cwd + '/rRsac_Tools.r'):
    r_library_loader(['rgdal','raster','maptools'])
    r('rast = raster("'+raster+'")')
    r('pt = readShapePoints("'+shapefile+'")')
    r('coords = (coordinates(pt)[,1:2])')
    values = r('extract(rast, coords)')
##    r1 = R()
##    r1.Rimport(rscript)
##    r1.r('print("hello")')
##    r2 = R(['raster', 'maptools', 'rgdal'])
##    values = r2.r('epv("' + shapefile + '", "' + raster + '")', True)
    return values
########################################################################################################################
#Extracts the raster value of a point shapefile and updates a specified field with the value in the shapefile
#Will add the field if it does not already exist using the following datatypes:
#Datatypes: Integer, Real, String, Float
def extract_value_to_shapefile(shapefile, field_name, raster, datatype = 'Integer'):
    add_field(shapefile, field_name, datatype)
    value_list = extract_value_to_list(shapefile, raster)
    update_field(shapefile, field_name, value_list)
    return value_list
########################################################################################################################
#Composites a list of images into a single raster
#If there are multiple images with data for a pixel, the value of the latest image in the list will be used
def composite(image_list, output, snap_raster, no_data = 0.0, dt = '', overwrite = True):
    if dt == '':
        info = raster_info(image_list[0])
        dt = info['dt']
    if os.path.exists(output) == False or overwrite == True:
        base = empty_raster(snap_raster, dt = dt)
        info = raster_info(snap_raster)
        height = info['height']
        width = info['width']
        counter = 100
        while counter > 0:
            for image in image_list:
                array = raster(image, dt = dt)
                for row in range(0, height, 1):
                    for column in range(0, width, 1):
                        pixel = array[row][column]
                        
                        if pixel != no_data:
                            base[row][column] = pixel
                        counter = counter -1
        write_raster(base, output, snap_raster, dt = dt)
    array = None
    base = None
########################################################################################################################
#Takes image list with the same extent, and places the value of the image in the order it is given if the value is
# greater than the data_range_min and less than the data_range_max
def smart_composite(image_list, output, data_range_min = 2, data_range_max = 253, dt = 'Int16'):
    info = raster_info(image_list[0])
    if dt == '':
        dt = info['dt']
    band_length = []
    for image in image_list:
        band_length.append(raster_info(image)['bands'])
    band_list = range(1, min(band_length) + 1)
        
    #base = empty_raster(image_list[0], dt = dt)
    base = brick(image_list[0], dt = dt, band_list = band_list)
    for image in image_list[1:]:
        array = brick(image, dt = dt, band_list = band_list)
        
        for bi in range(len(array)):
            band = array[bi]
           
            
            band[band < data_range_min] = -100
            band[band > data_range_max] = -100
            print numpy.maximum(band, base[bi])
            base[bi] = numpy.maximum(band, base[bi])

    write_raster(base, output, image_list[0], bands = min(band_length))
    array = None
    base = None
    band = None
########################################################################################################################     
#Downloads, snaps, and clips a dem to the extent of a provided raster
def dem_clip(extent_raster, output, dem_source = '//166.2.126.214/Data/National/Terrain/NED/grid/',
             res = '10', zone = '18', datum = 'WGS84', Buffer = 1000, create_mosaic = True, mask_output = True,
             dt = '', n_s_hemisphere = 'n', e_w_hemisphere = 'w', image_prefix = 'grd', overwrite = False):
    try:
        os.listdir(dem_source)
    except:
        print 'Please log onto:', dem_source
        raw_input('Press enter to continue')
    if os.path.splitext(extent_raster)[1] == '.shp':
        info = shape_info(extent_raster, False)
    else:
        info = raster_info(extent_raster)
    zone =  float(info['zone'])
    coords = info['coords']
    coords = buffer_coords(coords, Buffer)
    gdal_coords = coords_to_gdal(coords)
    print zone
    res = str(res)
    lat_lon_max =  utm_to_geog(zone, coords[0], coords[3])
    lat_lon_min = utm_to_geog(zone, coords[2], coords[1])
    print 'min',lat_lon_min
    print 'max',lat_lon_max
    
    lat_range = range(math.floor(float(lat_lon_min[0])), math.ceil(float(lat_lon_max[0])) + 1)
    lon_range = range(abs(math.ceil(float(lat_lon_min[1]))), abs(math.floor(float(lat_lon_max[1]))) + 1)

    tile_dirs = []
    for lat in lat_range:
        for lon in lon_range:
            if len(str(lat)) == 1:
                lat = '0' + str(lat)
            while len(str(lon)) < 3:
                lon = '0' + str(lon)
            if len(str(lon)) == 2:
                lat = '0' + str(lat)
            tile_dir = dem_source + n_s_hemisphere + str(lat) + e_w_hemisphere + str(lon) + '/'
            if os.path.exists(tile_dir) == True:
                tile_dirs.append(tile_dir )
            else:
                print 'oops', tile_dir
    image_list = []
    for tile_dir in tile_dirs:
        print os.path.basename(tile_dir)
        print tile_dir
        files = os.listdir(tile_dir)
        for File in files:
            looking_for = image_prefix + os.path.basename(tile_dir)
            
            if File.find(looking_for) > -1:
                image_list.append(tile_dir + File)

       
    print 'There are', len(image_list),'images to download and mosaic'
    if mask_output == True:
        temp_dir =os.path.dirname(output) + '/temp/'
        if os.path.exists(temp_dir) == False:
            os.makedirs(temp_dir)
        temp = temp_dir + os.path.splitext(output)[0].split('/')[-1]  + '_unclipped.img'
        
    else:
        temp = output
    if create_mosaic == True:             
        if os.path.exists(temp) == False:
        
            reproject(image_list, temp, clip_extent = gdal_coords, dt = dt, res = res, zone = zone, datum = datum, resampling_method = 'cubic')

        if os.path.splitext(extent_raster)[1] == '.shp' and mask_output == True:
          
            mask_rast = temp_dir + os.path.basename(os.path.splitext(extent_raster)[0]) + '_i.img'
            if os.path.exists(mask_rast) == False:
                shapefile_to_raster(extent_raster, mask_rast, temp, resolution = res)
        elif mask_output == True:
            mask_rast = extent_raster
                
        if mask_output == True:
            if os.path.exists(output) == False:
                info = raster_info(temp)
                mask(temp, mask_rast, output, dt = info['dt'], overwrite = overwrite)
    return image_list, coords
########################################################################################################################
#Calculates several terrain derivatives from a provided DEM using the gdaldem.exe program
def dem_derivatives(dem, out_dir, gdal_dir = gdal_dir, derivative_list = ['slope', 'aspect', 'roughness', 'hillshade', 'TPI', 'TRI'], overwrite = False):
    deriv_list = []
    print dem
    for derivative in derivative_list:
        output = os.path.splitext(dem)[0] + '_'+derivative+'.img'
        if os.path.exists(output) == False or overwrite == True:
            print 'Computing: ', derivative
            call = subprocess.Popen(gdal_dir + 'gdaldem '+derivative+' -of HFA ' + dem + ' ' + output)
            call.wait()
            print
        deriv_list.append(output)
    return deriv_list
######################################################################################
def nlcd_clip(extent_raster, output, nlcd_source = 'Q:/Programs/RSSC/fy2012/Projects/10025_R&D_Thermal_Mapping/02_Data-Archive/02_Inputs/Ancillary/Rasters/nlcd2006_landcover_2-14-11.img', proj = 'utm', datum = 'WGS84', res = '', zone = '', resampling_method = 'near', mask_output = True, overwrite = False):
    info = raster_info(extent_raster)
    if res == '':
        res = info['res']
    if zone == '':
        zone = info['zone']
    coords = info['gdal_coords']

    if mask_output == True:
        temp_dir =os.path.dirname(output) + '/temp/'
        if os.path.exists(temp_dir) == False:
            os.makedirs(temp_dir)
            
        
        
        temp = temp_dir + os.path.splitext(output)[0].split('/')[-1]  + '_unclipped.img'
    else:
        temp = output
    reproject(nlcd_source, temp, proj = proj, zone = zone, clip_extent = coords, datum = datum, res = res, resampling_method = resampling_method)
    if mask_output == True:
        if os.path.exists(output) == False:
            info = raster_info(temp)
            mask(temp, extent_raster, output, dt = info['dt'], overwrite = overwrite)
######################################################################################
#Prompts the user to enter a sample number for the stratified_random_sampler
def sample_no_getter():
    #print 'Please enter a list of samples count per strata. e.g. For a five class raster : 10,15,11,9,20:'
    #sample_no = raw_input()

    sample_no = askstring('Sample Count Entry', 'Please enter a list of samples count per strata. e.g. '\
                          'For a five class raster : 10,15,11,9,20:')
    
    
    #sample_no = list(sample_no)
    sample_no = sample_no.split(',')
    sample_no_temp = []
    for sample in sample_no:
        index = 0
        sample_temp = ''
        for char in sample:
            if char != ' ':
                sample_temp = sample_temp + char
        sample_no_temp.append(sample_temp)
    
    sample_no = sample_no_temp
    sample_no_temp = []
    try:
        for sample in sample_no:
            sample_no_temp.append(int(sample))
        sample_no = sample_no_temp
        if sample_no[-1] == ',':
            sample_no == sample_no[:-1]
    except:
        print 'Encountered string variable.  All entered sample counts must be integers'
        raw_input('Must restart program.  Press enter to exit')
        sys.exit()
    print sample_no
    
   
    return sample_no

######################################################################################
#Converts a list of x,y coordinates to a shapefile
#Snaps the location to the centroid of a snap raster's pixel locations
def list_to_point_shapefile(xy_coord_list, snap_raster = '', output = '', prj = '',dt = 'Byte'):
    print 'Creating', output.split('/')[-1]
    if snap_raster != '':
        info = raster_info(snap_raster)
        projection = info['projection']
    
    elif prj !='':
        projection = prj

    
    #Project it
    prj = os.path.splitext(output)[0] + '.prj'
    if os.path.exists(projection) == True:
        shutil.copy(projection, prj)
    else:
        prj_open = open(prj, 'w')
        prj_open.writelines(projection)
        prj_open.close()
        
    
    # get the driver
    driver = ogr.GetDriverByName('ESRI Shapefile')
    # create a new data source and layer
    if os.path.exists(output):
        driver.DeleteDataSource(output) 
    ds = driver.CreateDataSource(output)
    
    if ds is None:
        print 'Could not create file'
        sys.exit(1)
    layer = ds.CreateLayer(os.path.splitext(output)[0].split('/')[-1], geom_type=ogr.wkbMultiPoint)

    
    i = 1
    xs = []
    ys = []
    for coord in xy_coord_list:
        multipoint = ogr.Geometry(ogr.wkbMultiPoint)

        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(coord[0], coord[1])
        
        multipoint.AddGeometry(point)
        point.Destroy() 

        featureDefn = layer.GetLayerDefn() 

        feature = ogr.Feature(featureDefn)
        feature.SetGeometry(multipoint)
        xs.append(float(coord[0]))
        ys.append(float(coord[1]))


        layer.CreateFeature(feature)
        i += 1
 
    
    feature.Destroy()
    ds.Destroy()
  
    ds = None
    add_field(output, 'x', datatype = 'Real')
    add_field(output, 'y', datatype = 'Real')
    update_field(output, 'x', xs)
    update_field(output, 'y', ys)
######################################################################################
#Computes a normalized difference index for a stack
#Some common Landsat TM ndi's are:
#ndvi: band1 = 4, band2 = 3
#nbr: band1 = 4, band2 = 6 (or 7 if TIR is left in the stack) (default)
#vig: band1 = 2, band2 = 3
#ndmi: band1 = 4, band2 = 5
def ndi(stack, output, band1 = 4, band2 = 6, clip_raster = '', overwrite = False):
    if os.path.exists(output) == False or overwrite == True:
        print
        print
        print 'Computing:', os.path.basename(output)
        print 'Using bands:', band1, band2
        b1 = raster(stack, dt = 'Float32', band_no = band1)
        b2 = raster(stack, dt = 'Float32', band_no = band2)
        index = ((b1 - b2) / (b1 + b2)) * 1000.0
        if clip_raster != '':
            mask(index, clip_raster, output, dt = 'Int16')
        else:
            write_raster(index, output, stack, dt = 'Int16')
        b1 = None
        b2 = None
        index = None
    else:
        print output, 'already exists'
########################################################################################################################
#A function that produces several common indices using the ndi function
#Can specify a different band_dict if the bands are of a different sensor
#Comb_dict should remain the same regardless of the sensor
def index_maker(stack, clip_raster = '', band_dict = {'blue': 1, 'green' : 2, 'red' : 3, 'nir' : 4, 'swir1' : 5, 'swir2' : 6}, index_list = ['nbr','ndvi', 'vig','ndmi'], overwrite = False):
    folder = os.path.dirname(stack) + '/'
    comb_dict = {'nbr': [band_dict['nir'],band_dict['swir2']],
                'ndvi': [band_dict['nir'],band_dict['red']],
                 'vig': [band_dict['green'],band_dict['red']],
                 'ndmi': [band_dict['nir'],band_dict['swir1']]
                 }
    for index in index_list:
        output = os.path.splitext(stack)[0] + '_' + index + '.img'
        ndi(stack, output, comb_dict[index][0], comb_dict[index][1], clip_raster, overwrite = overwrite)
########################################################################################################################
#Produces a stratified random sample using a provided strata raster
#The strata raster should begin with 1 and increment by 1 for each additional stratum
#All parameters are optional.  If left blank, a gui will pop up to enter each parameter
#If calling function from within Python shell, follow syntax below.  All parameters are optional from the shell
def stratified_sampler(image = '',sample_no = [], sample_name = '', dt = '', wo_replacement = True, overwrite_output = True):
    
    #Finds any missing parameteres
    if image == '':
        print '!!! Please select classified image \containing discrete classes of 1, 2, 3, 4.....!!!'
        image = str(askopenfilename(title = 'Select Strata Raster',filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
        print
        print
    if sample_no == []:
        print '!!! Please provide a number of samples for each class within image !!!'
        sample_no = sample_no_getter()
        print
        print

    if dt == '':
        info = raster_info(image)
        dt = info['dt']
    if numpy_or_gdal(dt) == 'numpy':
        
        dt = dt_converter(dt)
    numpy_dt = dt_converter(dt)
    gdal_dt = 'gdal.GDT_' + dt
    
    image_dir = ''
    image_path_pieces = image.split('/')
    for piece in image_path_pieces[:-1]:
        image_dir = image_dir + piece + '/'
    
    if sample_name == '':
        print '!!! Please select directory to place output samples !!!'
        sample_name = str(asksaveasfilename(title = 'Select output sample name',initialdir = image_dir,filetypes=[("IMAGINE","*.img"),("tif","*.tif")])) 
        print
        print
    
    extension = os.path.splitext(sample_name)
    print 'Creating stratified random sample for: ' + image
    print
    print
    
    
    

    if os.path.exists(sample_name) == False or overwrite_output == True:
        info = raster_info(image)
        coords = info['coords']
        res = info['resolution']
        #Opens up the image using GDAL
        strata = gdal.Open(image)
        #Finds the number of bands
        bands = strata.RasterCount
        #If there is more than one band, warn that only the first band will be sampled 
        if bands > 1:
            print 'Image contains multiple bands'
            print 'Can only sample the first band of an image'
            raw_input('Press enter to continue')
            
        #Finds the height and width of the raster
        width = strata.RasterXSize
        height = strata.RasterYSize
        
        
        #Converts the raster into a 2d array in memory
        band1 = strata.GetRasterBand(1)
        band1_pixels = band1.ReadAsArray().astype(numpy_dt)

        
        
        #Creates 2d array of zeros
        band1 = numpy.zeros([height, width], numpy_dt)
        #band1 = numpy.empty([height, width], dtype = int)

        #This section iterates through each pixel in the provided raster to identify each strata and place each individual
        #stratum in a separate table with x,y coordinates within the raster and a unique identifier
        index = 1
        unid = 0
        table = []
        for i in range(len(sample_no)):
            table.append([])
            
        for row in range(0, height, 1):
            for column in range(0, width, 1):
                pixel = str(band1_pixels[row][column])
                
                for index in range(1, len(sample_no) + 1):
                    
                    if pixel == str(index):
                        
                        table[index-1].append(str(row) + '\t' + str(column))
                        unid = unid + 1

        #Retrieves the projection, driver, and spatial information 
        geotransform = strata.GetGeoTransform()
        #print geotransform
        projection = strata.GetProjection()
        #Currently supports .tif and .img formats
        if extension == '.img':
            dn = 'HFA'
        else:
            dn = 'GTiff'
            extension = '.tif'
        driver = gdal.GetDriverByName(dn)
        band1_pixels = None
        strata = None
        del band1_pixels
        del strata
        #This section iterates through each class, calculates a random set of numbers within the range
        #of the length of the extracted pixels in that class, and populates the raster with the respective
        #class value of that pixel
        random_numbers = []
        unid = 1
        report_lines = ''
        report_lines = report_lines + 'Stratified Random Sample Report for: ' + image + '\nSample Class Code\tSample Number\n'
        for i in range(len(sample_no)):
              
            report_lines = report_lines + str(i + 1) + '\t' + str(sample_no[i]) + '\n'
        total = sum(sample_no)
        report_lines = report_lines + 'Sample Total:\t' + str(total) + '\n'
        report_filename = os.path.splitext(sample_name)[0] +  '_sample_report.txt'
        report = open(report_filename, 'w')
        report.writelines(report_lines)
        report.close()
        xy_coords = []
        try:
            print 'Generating random sample'
           
            for i in range(len(sample_no)):
                
                #report_lines = report_lines + str(i + 1) + '\t' + sample_no[i] + '\n'
                if wo_replacement == False:
                    random_numbers = (list(numpy.random.random_integers(0, len(table[i]), int(sample_no[i]))))
                elif wo_replacement == True:
                    random_numbers = (random.sample(range(len(table[i])), int(sample_no[i])))
              
                
                for number in random_numbers:
                    row = table[i][number].split('\t')[0]
                    column = table[i][number].split('\t')[1]
                    band1[int(row)][int(column)] = i + 1
                    x_coord = (int(column)* res) + int(coords[0]) + (0.5 * res)
                    y_coord = int(coords[3])- (int(row)* res) - (0.5 * res)            
                    xy_coords.append((x_coord, y_coord, i + 1))
                    #print i,int(coords[3])- (int(row)* res) , (int(column)* res) + int(coords[0])
                    
                    unid = unid + 1
               
            list_to_point_shapefile(xy_coords, image, os.path.splitext(sample_name)[0] + '.shp')
        except:
            
            print 'Encountered error. Sample size is likely larger than pixel count for a class', i + 1
            warning = showwarning('Encountered Error!', 'Sample size is likely larger than pixel count for a class ' + str(i + 1))
            #raw_input('Press enter to exit and restart the program')
            sys.exit()
        
        
        #Creates new raster
        
        dst_ds = driver.Create(os.path.splitext(sample_name)[0] + '.img', width, height, bands, eval(gdal_dt))
        #Sets the projection and spatial info on the output raster
        dst_ds.SetProjection(projection)
        dst_ds.SetGeoTransform(geotransform) 
        dst_ds.GetRasterBand(1).WriteArray(band1)
        
        dst_ds = None
        band1 = None
        
        del dst_ds
        del band1
        print 'Finished creating raw random sample raster'
        print
        print
        return sample_name
########################################################################################################
#The following functions are used to perform several quadrangle-based functions
#The primary intended purpose of these functions is to take a shapefile or raster, and find all quadrangles
#that intersect it
#It then will search through a given list of directories for a specified set of key words and return the list of
#folders with the key words
#This workflow can be tweaked to work with NAIP image servers or any quadrangle-based imagery
########################################################################################################
def in2cm(inches):
    return float(inches)*2.54
def cm2in(cm):
    return float(cm)/2.54
def window_size_to_image_resolution(window_height, window_width, footprint_height, footprint_width, screen_resolution = 96, window_units = 'in', footprint_units = 'meters'):
    standard_units = ['inch', 'inches', 'in', 'in.', 'Inch', 'Inches', 'In', 'In.']
    
    if window_units in standard_units:
        window_type = 'imperial'
        window_height = in2cm(window_height)
        window_width = in2cm(window_width)
        screen_resolution = cm2in(screen_resolution)
    else:
        window_type = 'metric'
    if footprint_units in standard_units:
        footprint_type = 'imperial'
        footprint_height = in2cm(footprint_height)
        footprint_width = in2cm(footprint_width)
    else:
        footprint_type = 'metric'
    if footprint_units == 'meters':
        footprint_width = footprint_width * 100
        footprint_height = footprint_height * 100
    print window_height, window_width
    print footprint_height, footprint_width
    print screen_resolution
    pix_width = window_width * screen_resolution
    pix_height = window_height * screen_resolution
    print pix_width, pix_height
    res_x = footprint_width / pix_width
    res_y = footprint_height / pix_height
    return [res_x/100, res_y/100]
############################################################################
def circle(size):
    x_list = []
    y_list = []
    c = math.pi * size
    ct = int(c)*8
    matrix = numpy.zeros([size,size], int)
    for i in range(1, ct + 1,1):
        x_list.append((math.sin(i) + 1)/2)
        y_list.append((math.cos(i)+1)/2)
        
    
    for i in range(ct):
        matrix[int(size * y_list[i])][int(size * x_list[i])] = 1
    return matrix
def divide_list(List, divide_by):
    out_list = []
    for num in List:
        out_list.append(float(num)/float(divide_by))
    return out_list
def simple_circle(size):
    xs_temp = range(0,6350, 25)
    ys_temp = range(0, 6350, 25)
    xs = divide_list(xs_temp, 1000)
    ys = divide_list(ys_temp, 1000)
    x_list = []
    y_list = []
    for x in xs:
        x_list.append((math.sin(x)+ 1.0)/2* size)
    for y in ys:
        y_list.append((math.cos(y)+ 1.0)/2 * size)
    out_list = []
    for i in range(len(x_list)):
        out_list.append([x_list[i], y_list[i]])
    return out_list
##############################################################
def plot_burner(image, output, color = 'yellow', plot_size = 105, shape = 'circle', transparent = False, color_transparency = 0.2):
    if transparent == True:
        ct= 1.0- color_transparency
    else:
        ct = 1
    color_dict = {'yellow': [ct, ct, 0, ct],
                  'red' :[ct, 0,0,ct],
                  'blue': [0,0, ct, 0],
                  'cyan':[0,ct,ct,0],
                  'white' :[ct,ct,ct,ct,ct],
                  'black':[-ct,-ct,-ct,-ct],
                  'green':[0,ct, 0,0]
                  }
    color_scale = color_dict[color]
    info = raster_info(image)
    dt_range = info['dt_range']
    
    size = math.ceil(plot_size/ info['res'])
    array_list = []
    bands = info['bands']
    width =  info['width']
    height = info['height']
    center = [math.ceil(width/2), math.ceil(height/2)]
    row_start = center[1] - size/2
    row_end = center[1] + size/2
    column_start = center[0] - size/2
    column_end = center[0] + size/2

    
    i = 0
    for band in range(1,bands + 1, 1):
        array = raster(image, dt = info['dt'], band_no = band)

        if shape.find('are') > -1:
            for row in [row_start, row_end]:
                for column in range(column_start, column_end + 1, 1):
                    if transparent == True:
                        recode = array[row][column] + (array[row][column] * color_scale[i])
                        if recode < dt_range[0]:
                            recode = dt_range[0]
                        elif recode > dt_range[1]:
                            recode = dt_range[1]
                        array[row][column] = recode
                    else:
                        array[row][column] = color_scale[i] * dt_range[1]
            for column in [column_start, column_end]:
                for row in range(row_start, row_end + 1, 1):
                    if transparent == True:
                        recode = array[row][column] + (array[row][column] * color_scale[i])
                        if recode < dt_range[0]:
                            recode = dt_range[0]
                        elif recode > dt_range[1]:
                            recode = dt_range[1]
                        array[row][column] = recode
                    else:
                        array[row][column] = color_scale[i] * dt_range[1]
        else:
            matrix = circle(size)
            
            row_i = 0
            for row in range(row_start, row_end, 1):
                column_i = 0
                for column in range(column_start, column_end, 1):
                    
                    if matrix[row_i][column_i] == 1:
                        if transparent == True:
                            recode = array[row][column] + (array[row][column] * color_scale[i])
                            if recode < dt_range[0]:
                                recode = dt_range[0]
                            elif recode > dt_range[1]:
                                recode = dt_range[1]
                            array[row][column] = recode
                        else:
                            array[row][column] = color_scale[i] * dt_range[1]
                    column_i += 1
                row_i += 1
        i += 1
        array_list.append(array)
    array = None
    stack(array_list, output, image, array_list = True, dt = info['dt'],df = 'GTiff')
    array_list = None

############################################################################
def point_shp_to_quads(shapefile, out_folder , extent_height = 10000, extent_width = 10000, id_field_list = ['ID'],state_list = ['Indiana','Michigan', 'Minnesota','Wisconsin'], nas_list = [], doqq_key = 'DOQQ', window_height = '', window_width = '', screen_resolution = 96, plot_size= 80, zone = '', res = '', clip_to_extent = True, resampling_method = 'cubic', Format = 'HFA', mosaic_only = True, retain_original_projection = True,overwrite = False, negative_buffer = 0):
    info = shape_info(shapefile, False)
    format_dict = {'GTiff': '.tif', 'HFA': '.img'}
    extension = format_dict[Format]
    if info['zone'] == '':
        temp = shapefile
        shapefile = os.path.splitext(shapefile)[0] + '_UTM_Zone_' + str(zone) + '.shp'
        if os.path.exists(shapefile) == False:
            reproject_shapefile(temp, shapefile, zone = str(zone))
    
    db = dbf.Dbf(os.path.splitext(shapefile)[0] + '.dbf', ignoreErrors = True)
    id_list = []
    for row in range(len(db)):
        temp = []
        for id_field in id_field_list:
            temp.append(db[row][id_field])
        id_list.append(temp)
    db.close()
    plots = xy_coords(shapefile, False)
    if res == '':
        res = window_size_to_image_resolution(window_height, window_width, extent_height, extent_width, screen_resolution = screen_resolution)[0]
    
    i = 0
    for plot in plots:
        x = plot[0]
        y = plot[1]
        xmin = x - (0.5 * extent_width)
        xmax = x + (0.5 * extent_width)
        ymin = y - (0.5 * extent_height)
        ymax = y + (0.5 * extent_height)
        coords = [xmin, ymin, xmax, ymax]
        
        
        
        output = out_folder + 'Plot_'
        for ID in id_list[i]:
            output += str(ID) + '_'
        output+= 'NAIP_'+ str(extent_height)+extension
        burned_output = os.path.splitext(output)[0] + '_burned' + extension
        if os.path.exists(output) == False:
            quad_downloader(coords, output, state_list = state_list, nas_list = nas_list, doqq_key = doqq_key, zone = zone, res = str(res), clip_to_extent = clip_to_extent, resampling_method = resampling_method, Format = Format, mosaic_only = mosaic_only, retain_original_projection = False,overwrite = False, negative_buffer = 0)
        if os.path.exists(burned_output) == False:
            plot_burner(output, burned_output, plot_size = plot_size)
        i += 1
############################################################################
########################################################################################################
#Function finds all quad coordinates within a specified geographic size starting at a seed location
#Default settings reflect the standard 7.5 minute quadrangle size (0.125 or 1/8 degree) that begins at 0 lat, 0 long
#Function returns a list of long, lat coordinates of quads
#Input coordinates format = [xmin, ymin, xmax, ymax]
def quad_coords(coordinates, size_x = 0.125, size_y = 0.125, seedx = 0.0, seedy = 0.0):
    western_hemisphere = coordinates[1] < 0
    print coordinates
    seedx = int(seedx * 1000)
    seedy = int(seedy * 1000)
    size_x = int(size_x * 1000)
    size_y = int(size_y * 1000)
    coordinates = [int(coordinates[0] *1000),int(coordinates[1] *1000),int(coordinates[2] *1000),int(coordinates[3] *1000)]
 
    xs = range(seedx, int(math.ceil(coordinates[2])), size_x)
    ys = range(seedy, int(abs(math.ceil(coordinates[1]))) + size_y, size_y)

    i = 0
    for x in xs:
        if x > (coordinates[0] - size_x):
            xs = xs[i:]
            break
        i += 1
    i = 0
    for y in ys:
        
        if y  > (abs(coordinates[3])):
            ys = ys[i:]
            break
        i += 1
    print ys
    print xs
    out_coords = []
    for x in xs:
        x_cent = float(x) + (float(size_x)/2)
        for y in ys:
            y_cent = float(y) - (float(size_y)/2)
    
            out_coords.append([x_cent/1000, y_cent/1000])

            

    return out_coords
###########################################################
#Fuction that finds which quad number the quadrangle is within the standard NAIP numbering convention
#The standard convention divides a geographic degree into an 8x8 grid of quadrangles
#The number of the individual quadrangle within the degree is incremented from the upper left corner
#to the lower right corner
#This is similar to an array flatten function
#Ex: Quad [2,1] would be on the first column of the second row
#    With a 0.125 degree quad size, the quad number returned would be 9-
#    8 for the first row plus 1 for the first column of the second row
#    Quad [3,2] = (8 * 2) + 2 = 18.....
#Function returns the integer quad number
def which_quad(coords, x_size = 0.125, y_size = 0.125):

    quads_x =  1.0/x_size
    quads_y = 1.0/y_size

    x_size = x_size * 1000.0
    y_size = y_size * 1000.0

    x_dec = int(str(coords[1]).split('.')[1][:-1])
    y_dec = int(str(coords[0]).split('.')[1][:-1])
    
    x_coord = coords[1]*1000.0
    y_coord = coords[0] * 1000.0
 
    poss_x = range(int(0 + (0.5 * x_size)), int(1000 + (0.5 * x_size)), int(x_size))
    poss_y = range(int(0 + (0.5 * y_size)), int(1000 + (0.5 * y_size)), int(y_size))

    i = 1
  
    for poss in poss_x:
        if x_dec == poss:
            x_pos = i
            break
        i += 1
    i = 1

    for poss in poss_y:
        if y_dec == poss:
            y_pos = i
            break
        i += 1

    add_x = len(poss_x) + 1 - x_pos
    add_y = (len(poss_y) - y_pos) * len(poss_y)
    which = add_x + add_y
    return which
###########################################################
#Geographic minimum bounding rectangle coordinates of states
#Derived from a NAD83 Datum GCS83 Coordinate (geographic) state shapefile
#Intended to provide the state any vector or raster intersects
def state_mbr_coords(state = ''):
    state_mbr_dict = {"Alabama" : [-88.772023010253875, 29.889622879028281, -84.59347839355469, 35.308880615234344],
    "Alaska" : [-179.43337707519532, 50.91723937988278, 180.08820800781254, 71.698048400878875],
    "Arizona" : [-115.11539916992187, 31.029174041748046, -108.74486846923828, 37.304585266113278],
    "Arkansas" : [-94.918148803710935, 32.7045280456543, -89.344401550292972, 36.799656677246091],
    "California" : [-124.7111785888672, 32.230426025390642, -113.82947845458982, 42.309826660156233],
    "Colorado" : [-109.36079864501953, 36.692225646972659, -101.74196929931641, 41.305611419677732],
    "Connecticut" : [-74.029713439941347, 40.682486724853561, -71.48823089599604, 42.349732208251979],
    "Delaware" : [-76.088047790527341, 38.14932556152344, -74.742388916015628, 40.140576171874997],
    "District_of_Columbia" : [-77.42049865722656, 38.501475524902347, -76.609690856933597, 39.295063781738278],
    "Florida" : [-87.937222290039088, 24.21832199096681, -79.729006958007844, 31.302105712890587],
    "Georgia" : [-85.905499267578122, 30.057130050659179, -80.541949462890599, 35.302037048339827],
    "Hawaii" : [-160.53605346679691, 18.61549301147463, -154.49856872558593, 22.534394073486364],
    "Idaho" : [-117.54018859863281, 41.689837646484378, -110.74360961914063, 49.301522064208982],
    "Illinois" : [-91.812619018554656, 36.671115112304705, -86.718066406250003, 42.809479522705089],
    "Indiana" : [-88.389729309082028, 37.473048400878909, -84.487658691406281, 42.06232147216793],
    "Iowa" : [-96.935658264160153, 40.074542236328128, -89.839297485351565, 43.804646301269528],
    "Kansas" : [-102.34853820800781, 36.692221832275393, -94.292727661132815, 40.304512786865232],
    "Kentucky" : [-89.873669433593776, 36.196719360351544, -81.664187622070315, 39.447232055664095],
    "Louisiana" : [-94.345768737792937, 28.618104171752904, -88.514048767089847, 33.320599365234372],
    "Maine" : [-71.381993103027341, 42.764773559570301, -66.653987121582006, 47.761883544921858],
    "Maryland" : [-79.787136840820338, 37.61142272949219, -74.745890808105415, 40.024014282226595],
    "Massachusetts" : [-73.808399963378875, 40.93700332641604, -69.625392150878938, 43.186661529541027],
    "Michigan" : [-90.718701171874997, 41.39580078125001, -81.822886657714875, 48.604248809814422],
    "Minnesota" : [-97.538967895507781, 43.20210189819332, -89.187739562988313, 49.685620117187469],
    "Mississippi" : [-91.95424346923825, 29.874402236938472, -87.79795379638675, 35.298321533203115],
    "Missouri" : [-96.074398803710935, 35.695090484619143, -88.800578308105472, 40.91402893066406],
    "Montana" : [-116.35072784423828, 44.057688903808597, -103.73970336914063, 49.301808166503903],
    "Nebraska" : [-104.3528335571289, 39.699885559082034, -95.007991027832034, 43.3027961730957],
    "Nevada" : [-120.30534057617187, 34.702079010009768, -113.7393295288086, 42.300312805175778],
    "New_Hampshire" : [-72.856419372558591, 42.397776794433597, -70.413493347167972, 45.60873107910156],
    "New_Jersey" : [-75.867588806152341, 38.625640106201161, -73.593623352050784, 41.657639312744152],
    "New_Mexico" : [-109.35008697509765, 31.031899642944335, -102.70064849853516, 37.299423980712888],
    "New_York" : [-80.063320922851588, 40.199076843261764, -71.555873107910131, 45.317364501953143],
    "North_Carolina" : [-84.620960998535125, 33.544467163085926, -75.159487915039008, 36.889008331298868],
    "North_Dakota" : [-104.34958343505859, 45.635050964355472, -96.255137634277347, 49.301316070556638],
    "Ohio" : [-85.119923400878875, 38.102500152587922, -80.213862609863313, 42.624424743652312],
    "Oklahoma" : [-103.30086212158203, 33.315253448486331, -94.130686950683597, 37.30093078613281],
    "Oregon" : [-124.86600952148434, 41.692462158203114, -116.16163177490236, 46.58576278686526],
    "Pennsylvania" : [-80.81954650878906, 39.419429016113313, -74.390017700195315, 42.810452270507838],
    "Puerto_Rico" : [-68.252423095703122, 17.584189605712908, -64.92084808349604, 18.816252517700228],
    "Rhode_Island" : [-72.188359069824159, 40.844325256347702, -70.820597839355443, 42.319100189208996],
    "South_Carolina" : [-83.654339599609372, 31.749209594726583, -78.253672790527375, 35.516110229492149],
    "South_Dakota" : [-104.35712127685547, 42.181113433837893, -96.13656921386719, 46.244362640380857],
    "Tennessee" : [-90.610737609863278, 34.6838981628418, -81.347438049316409, 36.979244995117185],
    "Texas" : [-106.94576721191409, 25.538020324707045, -93.208728027343696, 36.803440856933612],
    "U.S._Virgin_Islands" : [-65.385670471191403, 17.37469215393066, -64.266146850585883, 18.712990570068367],
    "Utah" : [-114.35406188964843, 36.698630523681643, -108.74093933105469, 42.304196166992185],
    "Vermont" : [-73.743420410156247, 42.42761154174805, -71.16769714355469, 45.316334533691403],
    "Virginia" : [-83.974812316894557, 36.239142608642545, -74.940707397460969, 39.766579437255857],
    "Washington" : [-125.05578308105464, 45.253112030029293, -116.61249847412108, 49.303620147705089],
    "West_Virginia" : [-82.940769958496091, 36.902762603759768, -77.419718933105472, 40.938553619384763],
    "Wisconsin" : [-93.185383605957057, 42.194701385498064, -85.949557495117133, 47.602532196044912],
    "Wyoming" : [-111.35513000488281, 40.696269226074222, -103.75197906494141, 45.304203796386716]}
    try:
        return state_mbr_dict[state]
    except:
        return state_mbr_dict
def intersects(coords1, coords2):
    i = False
    corners = [[coords1[0], coords1[1]], [coords1[2], coords1[3]], [coords1[0], coords1[3]], [coords1[2], coords1[1]]]
    for corner in corners:
        if corner[0] > coords2[0] and corner[0] < coords2[2] and corner[1] > coords2[1] and corner[1] < coords2[3]:
            i = True
    return i
def state_intersect(coords):
    state_list = []
    state_dict = state_mbr_coords()
    for state in state_dict:
        ct = state_dict[state]
        i = intersects(coords, ct)
        if i == True:
            state_list.append(state)
    return state_list
###########################################################
#The following functions are used to search through a list of key words and directories
#This function will append a key to a list of directories from the nas_dir_getter function if needed
#Returns an updated key: directory dictionary containing the key appended to the directory
def state_dirs_to_doqq_dirs(state_dir_dict, doqq_key = 'DOQQ'):
    out_list = []
    for Dir in state_dir_dict:
        sub_dirs = os.listdir(state_dir_dict[Dir])
        for sub in sub_dirs:
            if type(doqq_key) == list:
                key_no = 1
                for key in doqq_key:
                    if sub.find(key) > -1:
                        out_list.append([Dir + '_' + str(key_no), state_dir_dict[Dir] + sub + '/'])
                    key_no += 1
            else:
                if sub.find(doqq_key) > -1:
                    out_list.append([Dir, state_dir_dict[Dir] + sub + '/'])
    
    return dict(out_list)
###########################################################
def walker(directory, out_list = [], levels = 2):
    if directory[-1] == '/':
        directory = directory[:-1]
    if levels > 0:
        levels = levels - 1
        
        Dirs = os.listdir(directory)
        for Dir in Dirs:
            
            out_list.append(str(directory) + '/' + str(Dir))
            walker(directory + '/' + Dir, out_list, levels)
            levels = levels - 1
    else:
      
        global walker_dirs
        walker_dirs = out_list

#This function searches through a list of directories for a list of key words
#A dictionary is returned with the key word as the key and its respective directory as the definition
#Only one directory is assigned to each key- the first directory found containing the key
def nas_dir_getter(key_list = ['Minnesota', 'Michigan', 'Wisconsin'], nas_list = ['//166.2.126.33/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/','//166.2.126.23/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/', '//166.2.126.19/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/'], dir_levels = 3):
    key_count = len(key_list)
    out_dict = []

        
    for nas in nas_list:
        
        try:
            dirs = os.listdir(nas)
        except:
            print 'Please log onto:', nas
            raw_input('Press enter to continue')
        walker(nas, [],dir_levels)
        
        for Dir in walker_dirs:
            for key in key_list:
                if Dir.find(key) > -1:
                    if Dir[-1] != '/':
                        Dir = Dir + '/'
                    out_dict.append([key, Dir])
                    if len(out_dict) == len(key_list):
                        
                        return dict(out_dict)

#This function combines the functions above
#This function should be used when finding NAIP directories on the NAS
def get_doqq_dirs(key_list = ['Minnesota', 'Michigan', 'Wisconsin'], nas_list = ['//166.2.126.33/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/','//166.2.126.23/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/', '//166.2.126.19/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/'], doqq_key = 'DOQQ'):
    Dict = nas_dir_getter(key_list, nas_list)
    
    out = state_dirs_to_doqq_dirs(Dict, doqq_key)
    return out

###########################################################
#This function takes a list of quad centroid coordinates (likely from quadd_coord function) and returns a list of image tiles
#The coord list must be geographic and coorespond to the naming convention of the nas_dirs
#If the quads are nested into a sub folder with the geographic degree being the name (as with NAIP), the the nested_degree_folder option must be True
#If the quads are located directly within the directories in the nas_dirs, the nested_degree_folder option must be False
def quad_getter(coord_list, nas_dirs = ['//166.2.126.19/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/2009_doqq/Michigan_2009_NAIP_doqqs/Michigan_Statewide_DOQQ_2009/'], nested_degree_folder = True, extension = '.tif'):
    quad_list = []
    for nas_dir in nas_dirs:
        print 'Reading:',nas_dir
        folders = os.listdir(nas_dir)
        
        for coord in coord_list:
          
            lat = str(coord[0])[:2]
            lon = str(int(coord[1]))
            lon_len = len(lon)
            while len(lon) < 3:
                lon = '0' + lon
            
            coord_folder = lat + lon
            
            which = str(which_quad(coord))
            if len(which) == 1:
                which = '0' + str(which)
          
            if coord_folder in folders:
                if nested_degree_folder == True:
                    folder = nas_dir + coord_folder + '/'
                else:
                    folder = nas_dir + '/'
                images = os.listdir(folder)
                for image in images:
                    if image.find(coord_folder + which) > -1 and os.path.splitext(image)[1] == extension:
                        quad_list.append(folder + image)
    return quad_list
###########################################################
def image_downloader(quad_list, out_folder, proj = 'utm', zone = '', datum = 'nad83' , res = '',resampling_method = 'cubic', clip_extent = '', Format = 'HFA', overwrite = False):
    format_dict = {'HFA': '.img', 'GTiff': '.tif'}
    extension = format_dict[Format]
    out_list = []
    for quad in quad_list:
        output = out_folder + os.path.splitext(os.path.basename(quad))[0] + '_' + res  + extension
        out_list.append(output)
        if os.path.exists(output) == False:
            reproject(quad, output, proj = proj, zone = zone, datum = datum, res = res, resampling_method = resampling_method, clip_extent = clip_extent, Format = Format)
        if os.path.exists(output) == True and overwrite == True:
            try:
                os.remove(output)
                reproject(quad, output, proj = proj, zone = zone, datum = datum, res = res, resampling_method = resampling_method, clip_extent = clip_extent, Format = Format)
            except:
                print 'Could not overwrite:', output
    return out_list
###########################################################
#This function combines all of the functions above into a single process
#The function will ensure the projection of the provided image or shapefile is retained if the retain_original_projection option is set to True
#Otherwise, it will inherit the projection of the tiles
#The state_list can be a list of states which the extent raster or shapefile may intersect
#The res option can be set to any resolution
def quad_downloader(extent_raster_or_shapefile, out_folder , state_list = [], 
                    nas_list = ['//166.2.126.33/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/','//166.2.126.23/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/', '//166.2.126.19/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/'], 
                    doqq_key = 'DOQQ',zone = '', res = '', datum = 'nad83',clip_to_extent = True, Buffer = 0, resampling_method = 'cubic', 
                    Format = 'HFA', mosaic_only = True, download_images = True, retain_original_projection = True,overwrite = False, negative_buffer = 0):
    if type(extent_raster_or_shapefile) == list:
        coords = extent_raster_or_shapefile
        gdal_coords = str(coords[0]) + ' ' + str(coords[1]) + ' ' + str(coords[2]) + ' ' + str(coords[3])
    else:
        if os.path.splitext(extent_raster_or_shapefile)[1] == '.shp':
            info = shape_info(extent_raster_or_shapefile, False)
        else:
            info = raster_info(extent_raster_or_shapefile)
        if zone == '':
            zone = int(info['zone'])
        coords = info['coords']
        
        gdal_coords = info['gdal_coords']
        datum = info['datum']

    
    print gdal_coords, datum
    ic = coords
    coords = buffer_coords(coords, Buffer)
    
    coords = [coords[0] + abs(negative_buffer),coords[1] + abs(negative_buffer), coords[2] - abs(negative_buffer),coords[3] - abs(negative_buffer)]
    gdal_out_coords = coords_to_gdal(coords)
    mins = utm_to_geog(int(zone), coords[0],coords[1])
    maxes = utm_to_geog(int(zone), coords[2],coords[3])
  
    coordinates = [mins[0], mins[1], maxes[0], maxes[1]]
    state_coords = [mins[1], mins[0], maxes[1], maxes[0]]
    #Find the states the shapefile intersects if a list is not provided
    if state_list == [] or state_list == '' or len(state_list) == 0:
        print 'Finding states that intersect', state_coords
        state_list = state_intersect(state_coords)
    print 'Searching NAS dirs for:', state_list
    
    print 'Finding quads that intersect image/shapefile', coordinates

    
    Dirs = get_doqq_dirs(state_list, nas_list = nas_list, doqq_key = doqq_key)
    dir_list = []
    for Dir in Dirs:
        dir_list.append(Dirs[Dir])
    print dir_list

    
    quads = quad_coords(coordinates)
    quad_list = quad_getter(quads, dir_list)
  
   
    print 'There are', len(quad_list), 'images to download'
    print zone
    if mosaic_only == True and download_images == True:
        if os.path.isdir(out_folder):
            output = out_folder + 'mosaic.img'
        else:
            output = out_folder
        if os.path.exists(output) == False or overwrite == True:
            #mosaic(quad_list, output, zone = zone, datum = datum, res = res, clip_extent = gdal_coords, resampling_method = resampling_method, Format = Format, reproject_image = retain_original_projection)
            reproject(quad_list, output, res = res, clip_extent = gdal_out_coords, resampling_method = resampling_method, Format = Format)
        return output
    elif download_images == True:
        outs = image_downloader(quad_list, out_folder, zone = str(zone), datum = datum, res = res, resampling_method = resampling_method, overwrite = overwrite)
        return outs
    else:
        
        return quad_list, coords


###########################################################
def union_extent_info(image_list, band_no = 1):
    coord_list = [[],[],[],[]]
    for image in image_list:
        info = raster_info(image, band_no)
        coords = info['coords']
        
        
        i  = 0
        for coord in coords:
            coord_list[i].append(coord)
            i += 1
    extent_coords = []
    for coords in coord_list[:2]:
        extent_coords.append(min(coords))
    for coords in coord_list[2:]:
        extent_coords.append(max(coords))
    res = info['res']
    projection = info['projection']
    dt = info['dt']
    bands = info['bands']
    datum = info['datum']
    numpy_dt = dt_converter(dt)
    
    transform = [extent_coords[0], res, 0.0, extent_coords[-1], 0.0, res * -1]
    width = int(math.ceil((extent_coords[2] - extent_coords[0])/ res))
    height = int(math.ceil((extent_coords[3] - extent_coords[1])/ res))
    return {'coords':extent_coords, 'transform': transform, 'res': res, 'width':width, 'height': height, 'projection': projection, 'dt': dt, 'numpy_dt' : numpy_dt, 'datum' : datum, 'bands': bands}
###########################################################
def merge(image_list, output, Format = 'HFA', image_limit = 23, no_data = '0', gdal_dir = gdal_dir):
    if Format != '':
        Format = '-of ' + str(Format) + ' ' 
    if no_data != '':
        no_data = '-n ' + str(no_data) + ' '
    gdal_call = '"' + gdal_dir + 'gdal_merge.py" -o ' + output + ' ' + no_data + Format
    for image in image_list[:image_limit]:
        if os.path.exists(image) == True:
            gdal_call += image + ' '
    gdal_call =  gdal_call[:-1]
    print gdal_call
    
    bat_lines =  ['c:\n']
    for i in range(10):
        bat_lines.append('cd.. \n')
    bat_lines.append(gdal_call + '\n')
   
    bat_filename = cwd + 'bat_temp.bat'
    print bat_filename
    bat_open = open(bat_filename, 'w')
    bat_open.writelines(bat_lines)
    bat_open.close()
    call = subprocess.Popen(bat_filename)
    call.wait()
    try:
        os.remove(bat_filename)
    except:
        print 'Could not remove', bat_filename
###########################################################
def mosaic(image_list, output, crs = '', proj = 'utm', zone = '', datum = 'nad83' , res = '',resampling_method = 'near', clip_extent = '', Format = 'HFA', overwrite = False, reproject_image = False, gdal_dir = gdal_dir):
    inputs = ''
    res_template = raster_info(image_list[0])['res']
    
    if float(res) > (res_template * 5):
        print 'Specified resolution '+res+' is > 5x original resolution', res, res_template * 5
        print 'Must first mosaic at 5x original resolution and then resample'
        res_1 = res_template * 5
        reproject_image = True
    else:
        res_1 = res
        
    for image in image_list:
        inputs += image + ' ' 
    inputs = inputs[:-1]
    if reproject_image == True:
        temp_output = os.path.splitext(output)[0] + '_orig_proj' + os.path.splitext(output)[1]
    else:
        temp_output = output
    if os.path.exists(temp_output) == False or overwrite == True:
        reproject(image_list, temp_output, proj = proj, zone = str(zone), datum = datum, res = res_1, resampling_method = resampling_method, clip_extent = clip_extent, Format = Format)
##    if Format != '':
##        ot = ' -of ' + Format
##    if res != '':
##        res_temp = ' -tr ' + str(res_1) + ' ' + str(res_1) + ' '
##    if clip_extent != '':
##        clip_extent = ' -te ' + clip_extent + ' '
##
##    gdal_call = gdal_dir + 'gdalwarp'+ ot + res_temp  + clip_extent + inputs + ' ' + temp_output
##    print gdal_call
##    print
##    if os.path.exists(temp_output) == False or overwrite == True:
##        call = subprocess.Popen(gdal_call)
##        call.wait()
    zone = str(zone)
    if (os.path.exists(output) == False or overwrite == True) and reproject_image == True:
        
        
        reproject(temp_output, output, proj = proj, zone = zone, datum = datum, res = res, resampling_method = resampling_method, clip_extent = clip_extent, Format = Format)
        


def mosaic_numpy(image_list, output, extent = '', band_no = 1, write_raster_output = True, eliminate_zeros = True):
    
    info = union_extent_info(image_list, band_no)
    
     

    res = info['res']
    
    u_ulxy = [info['coords'][0], info['coords'][-1]]
    bands = info['bands']
    array_list = []
    for band in range(1, bands + 1):
        empty_raster = numpy.zeros([info['height'], info['width']]).astype(info['numpy_dt'])
        print band
        for image in image_list:
          
            i_info = raster_info(image, band_no = band)
            width = i_info['width']
            height = i_info['height']
            coords = i_info['coords']
            dt = i_info['dt']
            i_ulxy = [coords[0], coords[-1]]

            d_x = int((i_ulxy[0] - u_ulxy[0])/ res)
            d_y = int((u_ulxy[1] - i_ulxy[1])/ res)

            array = raster(image, dt = dt, band_no = band)
           
            if eliminate_zeros == True:
                for row in array:
                    
                    #print nums
                    if max(row) == 0:
                        array = array[1:]
                        height = height -1
                        d_y = d_y + 1
            array_row = 0
            for row in range(d_y, d_y + height):
                array_column = 0
                for column in range(d_x, d_x + width):
                    pixel_value = array[array_row][array_column]
                    if eliminate_zeros == True:
                        if pixel_value != 0:
                            empty_raster[row][column] = pixel_value
                    else:
                        empty_raster[row][column] = pixel_value
                                              
##                    if pixel_value
##                    empty_raster[row][column]
##                    empty_raster[row][d_x: (d_x + width)] = array[array_row]
                    array_column += 1
                array_row += 1
           
        array_list.append(empty_raster)
    print info['projection'] 
    if write_raster_output == True:
        stack(array_list, output, dt = info['dt'], width = info['width'], height = info['height'], projection = info['projection'], transform = info['transform'], array_list = True)
    return array_list 
    empty_raster = None
    array = None
    array_list = None
#images = map(lambda i: Dir + i, filter(lambda i: i.find('3_5.img') > -1, os.listdir(Dir)))
########################################################################################################
##def quick_mosaic(image_list, output, coords, band_list = [], res = 30, df = 'HFA'):
##    res_min = 1000000
##    band_min = 100
##    for image in image_list:
##        info = raster_info(image)
##        projection, proj4, bands, res_t, coords_t =info['projection'],info['proj4'], info['bands'], info['res'], info['coords']
##        if band_min > bands:
##            band_min = bands
##        if res_min > res_t:
##            res_min = res_t
##    if res == '':
##        res = res_min
##    if len(band_list) == 0 or band_min < max(band_list):
##        bands = band_min
##        band_list = range(bands)
##    else:
##        bands = len(band_list)
##    bands = 1
##    dt = info['dt']
##    if numpy_or_gdal(dt) == 'numpy':
##        
##        dt = dt_converter(dt)
##    gdal_dt = 'gdal.GDT_' + dt
##    print coords
##    width = math.ceil(float((coords[2] - coords[0]))/float(res))
##    height = math.ceil(float((coords[3] - coords[1]))/float(res))
##    
##    print width, height, bands, output, gdal_dt
##    print projection
##    transform = [coords[0], float(res), 0.0, coords[3], 0.0, -1 * float(res)]
##    print transform
##    driver = gdal.GetDriverByName(df)
##    print 'Initiating output raster:', output
##    ds = driver.Create(output, float(width), height, str(bands), eval(gdal_dt))
##    print 'yay'
##    ds.SetProjection(projection)
##    ds.SetGeoTransform(transform)
##    array = brick(image_list[0])
##    write_raster(array, output, image_list[0])
##    
##    array = None
###########################################################################
def logistic_regression(working_directory, training_pts, binary_field, preds, output_name):
    training_pts = training_pts.split('/')[-1]
    predictors = 'c('
    for pred in preds:
        #pred = pred.split('/')[-1]
        predictors += '"' + pred + '", '
    predictors = predictors[:-3] + '")'
    inputs_dir = working_directory



    
    coeff = r2.r('logit_model("' + inputs_dir + '", "' + training_pts + '", '+binary_field+',' + predictors + ')', True)
    print coeff
    print preds[0]
    out = clip(preds[0], preds, zeros_only = True, dt = 'Float32')[0]



    for i in range(len(preds)):
        print 'Computing:'
        print preds[i].split('/')[-1] + ' * ' + str(coeff[i + 1])
        
        rast = clip(preds[i], preds)[0]
        print numpy.shape(rast)
        print numpy.shape(out)
        out += (rast * coeff[i +1])
        print
        print
        print
    print 'Computing:'
    print '1/(1 + e^-vb) + ' + str(coeff[0])
    print
    print
    out += (coeff[0])
    out = (1.0 / (1.0 + numpy.exp(-1.0 * out ))) * 1000.0
    write_raster(out, output_name, preds[0], dt = 'Int16')
    
######################################################################################
def raster_cubist(wd, training_pts, training_field_name, predictor_list = [], output = 'cubist_output.img', committees = 1, neighbors = 0, overwrite = False, rscript = cwd + 'rRsac_Tools.r'):
    predictors = 'c('
    for pred in predictor_list:
        predictors += '"' + os.path.basename(pred) + '", '
    predictors = predictors[:-3] + '")'
    training_pts = os.path.basename(training_pts)
    if wd[-1] == '/':
        wd = wd[:-1]
    call = 'raster_cubist("'+wd +'", "' + training_pts + '", '+training_field_name+', '+predictors+', "'+output+'", '+str(committees)+', '+str(neighbors)+')'
    if os.path.exists(output) == False or overwrite == True:
        r1 = R()
        r1.Rfun(rscript, call)
######################################################################################
def raster_svm(wd, training_pts, training_field_name, predictor_list = [], output = 'svm_output.img', overwrite = False, rscript = cwd + 'rRsac_Tools.r'):
    predictors = 'c('
    for pred in predictor_list:
        predictors += '"' + os.path.basename(pred) + '", '
    predictors = predictors[:-3] + '")'
    training_pts = os.path.basename(training_pts)
    if wd[-1] == '/':
        wd = wd[:-1]
    call = 'raster_svm("'+wd +'", training_points = "' + training_pts + '", training_field_name = '+training_field_name+', predictor_rasters = '+predictors+', output_name = "'+output+'")'
    if os.path.exists(output) == False or overwrite == True:
        r1 = R()
        r1.Rfun(rscript, call)
######################################################################################
def raster_rf(wd, training_pts, training_field_name, predictor_list = [], output = 'rf_output.img', overwrite = False, rscript = cwd + 'rRsac_Tools.r'):
    predictors = 'c('
    for pred in predictor_list:
        predictors += '"' + os.path.basename(pred) + '", '
    predictors = predictors[:-3] + '")'
    training_pts = os.path.basename(training_pts)
    if wd[-1] == '/':
        wd = wd[:-1]
    call = 'raster_rf("'+wd +'", training_points = "' + training_pts + '", training_field_name = '+training_field_name+', predictor_rasters = '+predictors+', output_name = "'+output+'")'
    if os.path.exists(output) == False or overwrite == True:
        r1 = R()
        r1.Rfun(rscript, call)
######################################################################################
def raster_caret(wd, training_pts, training_field_name, predictor_list = [], output = 'caret_output.img', overwrite = False, rscript = cwd + 'rRsac_Tools.r'):
    predictors = 'c('
    for pred in predictor_list:
        predictors += '"' + os.path.basename(pred) + '", '
    predictors = predictors[:-3] + '")'
    training_pts = os.path.basename(training_pts)
    if wd[-1] == '/':
        wd = wd[:-1]
    call = 'raster_caret("'+wd +'", training_points = "' + training_pts + '", training_field_name = '+training_field_name+', predictor_rasters = '+predictors+', output_name = "'+output+'")'
    if os.path.exists(output) == False or overwrite == True:
        r1 = R()
        r1.Rfun(rscript, call)

######################################################################################
def raster_boot_cv(wd, training_pts, training_field_name, predictor_list = [], output = 'boot_output.img', model_list = 'c("svm","rf","cubist")',method_list  = 'c("cv", "boot")', count_list = 'c(10, 15)', make_raster = 'TRUE',overwrite = False, rscript = cwd + 'rRsac_Tools.r'):
    predictors = 'c('
    for pred in predictor_list:
        predictors += '"' + os.path.basename(pred) + '", '
    predictors = predictors[:-3] + '")'
    training_pts = os.path.basename(training_pts)
    if wd[-1] == '/':
        wd = wd[:-1]
    call = 'raster_boot_cv("'+wd +'", training_points = "' + training_pts + '", training_field_name = '+training_field_name+', predictor_rasters = '+predictors+', output_name = "'+output+'", model_list = ' + model_list + ', method_list = ' + method_list + ', count_list = '+ count_list +', make_raster = ' +make_raster+')'
    if os.path.exists(output) == False or overwrite == True:
        r1 = R()
        r1.Rfun(rscript, call)
######################################################################################
#Removes any duplcate entries in a list
def remove_duplicates(combos):
    
    combos2 = combos
    for combo in combos:
        index = 0
        for combo2 in combos:
            if len(combo2) == len(combo) and combo != combo2:
                find_total = 0
                for part in combo2:
                    if part in combo:
                        find_total += 1
                if find_total == len(combo):
                    x = combos.pop(index)
                    
            index += 1
    return combos
######################################################################################
#Computes all combinations in a list of length n
def combinations(items, n):
    if n == 0:
        yield []
    else:
        for i in xrange(len(items)):
            for cc in combinations(items[:i] + items[i+1:], n-1):
                yield [items[i]] + cc
######################################################################################
def combo_n_list(List, n_list, remove_dups = True):
    out_list = []
    for n in n_list:
        for pm in combinations(List, n):
            out_list.append(pm)
    if remove_dups == True:
        out_list = remove_duplicates(out_list)
    return out_list
#########################################################################

out = None
rast = None
array = None

