#This script contains a library of functions that use various open source statistical and geospatial
#software packages to ease basic raster processing and modeling procedures
#This script was written with funding from a USDA Forest Service Remote Sensing
#Steering Commmittee project that used thermal data to model percent impervious

#This script was written by Ian Housman at the Forest Service Remote Sensing Applications Center
#ihousman@fs.fed.us
###############################################################################
#Import all necessary packages
import shutil, os, subprocess, sys, string, random, math, time, itertools, urllib, zipfile,gzip
from scipy.optimize import curve_fit
import scipy
from scipy import stats
###############################################################################
#Set based on whether R is needed
needs_r = False
###############################################################################
cwd = os.getcwd().replace('\\','/') + '/'
###############################################################################
#Set Python version and home directory
python_possibilities = {'C:\\Python27\\ArcGIS10.3': [27, 10.3],'C:\\Python27\\ArcGIS10.2': [27, 10.2],'C:\\Python27\\ArcGIS10.1': [27, 10.1],'C:\\Python26\\ArcGIS10.0': [26, 10], 'C:\\Python26': [26, 9.3],'C:\\Python25' : [25, 9.3]}
for possibility in python_possibilities:
    if os.path.exists(possibility):
        arc_version = python_possibilities[possibility][1]
        python_version =   python_possibilities[possibility][0]
        python_dir = possibility
        #break
###############################################################################
#Set up the gdal data and bin environment variable names
#Set up the gdal data and bin environment variable names
site_packages_dir = python_dir + '/Lib/site-packages/'
def setup_gdal_dirs():
    global gdal_bin_dir, gdal_data_dir, gdal, gdal_array, osr, ogr, gdalconst, path
    gdal_data_options = [site_packages_dir + 'gdalwin32-1.6/data', site_packages_dir + 'gdalwin32-1.9/bin/gdal-data']
    gdal_bin_options = [site_packages_dir + 'gdalwin32-1.6/bin', site_packages_dir + 'gdalwin32-1.9/bin']
    gdal_data_dir = ''
    gdal_bin_dir = ''
    for data_option in gdal_data_options:
        if os.path.exists(data_option):
            gdal_data_dir = data_option
    for bin_option in gdal_bin_options:
        if os.path.exists(bin_option):
            gdal_bin_dir = bin_option

    path = os.environ.get('PATH')
    if path[-1] != ';':
        path += ';'
    if gdal_data_dir != '':
        print 'Updating GDAL_DATA path variable'
        os.putenv('GDAL_DATA', gdal_data_dir)
    if gdal_bin_dir != '':
        print 'Updating path with GDAL bin location'
        path = path + gdal_bin_dir


        os.putenv('PATH',path)
        #print os.environ.get('PATH')
        os.chdir('c:\\windows\\system32')
        from osgeo import gdal
        from osgeo import gdal_array
        from osgeo import osr, ogr
        from osgeo import gdalconst
        os.chdir(cwd)
setup_gdal_dirs()
###############################################################################
#Let user know what the directories are
#(Arc version does not necessarily mean that Arc is installed)
print 'Arc version:',arc_version
print 'Python version:', python_version
print 'Python dir:', python_dir
print 'GDAL bin:', gdal_bin_dir
print 'GDAL data:', gdal_data_dir

python_version_dec = str(float(python_version)/10)
python_version = str(python_version)
admin = False

#############################################################################
#Find the program files dir
program_files_dir_options = ['C:/Program Files (x86)/', 'C:/Program Files/']
for option in program_files_dir_options:
    if os.path.exists(option):
        program_files_dir = option
        break
print 'Program files dir:', program_files_dir
#############################################################################
#Set up the gdal directory
gdal_dir = program_files_dir + 'FWTools2.4.7/bin/'
if os.path.exists(gdal_dir) == False:
    gdal_dir = cwd +  'FWTools2.4.7/bin/'

if os.path.exists(python_dir)==False:
    print 'Python version:', python_version, 'Arc version:', arc_version,'does not exist'
    raw_input('Press enter to exit')
    sys.exit()
#############################################################################
#Import some more packages
try:
    from tarfile import TarFile
except:
    import tarfile
import tarfile
from tkFileDialog import askopenfilename
from tkFileDialog import askopenfilenames
from tkFileDialog import askdirectory
from tkSimpleDialog import askstring
from tkMessageBox import showwarning
import tkMessageBox
from tkFileDialog import asksaveasfilename
################################################################
#Image format driver dictionary
format_dict =  {'.tif': 'GTiff', '.img' : 'HFA', '.jpg' : 'JPEG', '.gif' : 'GIF', '.grid' : 'AAIGrid', '.hdr': 'envi', '': 'envi','.ntf': 'NITF'}
formats_dict = format_dict
################################################################
def smart_unzip(Zip, base_dir = ''):
    z = zipfile.ZipFile(Zip)
    if base_dir == '':
        base_dir = cwd
    if base_dir[-1] != '/':
        base_dir += '/'
    for f in z.namelist():
        fbd = base_dir + f
        if f.endswith('/') and os.path.exists(fbd) == False:
            print 'Extracting', f
            os.makedirs(fbd)
        elif os.path.isdir(f) == False and os.path.exists(fbd) == False:
            print 'Extracting', f
            z.extract(f, base_dir)

################################################################
#Returns Windows version
def get_os_info():
    if os.name == 'nt':
        ver = os.sys.getwindowsversion()
        ver_format = ver[3], ver[0], ver[1]
        win_version = {
        (1, 4, 0): '95',
        (1, 4, 10): '98',
        (1, 4, 90): 'ME',
        (2, 4, 0): 'NT',
        (2, 5, 0): '2000',
        (2, 5, 1): 'XP',
        (2, 5, 2): '2003',
        (2, 6, 1): '7'
        }

    if win_version.has_key(ver_format):
        wv = win_version[ver_format]
        print 'Windows version:', wv
        return  win_version[ver_format]
    else:
        return '8?'
################################################################
#Define a function that can install various packages over the internet
def install(package_name, cleanup = False):
    install_packages = {'dbfpy':['http://sourceforge.net/projects/dbfpy/files/dbfpy/2.2.5/dbfpy-2.2.5.win32.exe/download', 'dbfpy-2.2.5.win32.exe'],
                        'numpy': ['http://sourceforge.net/projects/numpy/files/NumPy/1.6.1/numpy-1.6.1-win32-superpack-python'+python_version_dec+'.exe/download','numpy-1.6.1-win32-superpack-python'+python_version_dec+'.exe'],
                        'gdal' : ['http://pypi.python.org/packages/'+python_version_dec+'/G/GDAL/GDAL-1.6.1.win32-py'+python_version_dec+'.exe#md5=5e48c85a9ace1baad77dc26bb42ab4e1','GDAL-1.6.1.win32-py'+python_version_dec+'.exe'],
                        'rpy2' : ['http://pypi.python.org/packages/'+python_version_dec+'/r/rpy2/rpy2-2.0.8.win32-py'+python_version_dec+'.msi#md5=2c8d174862c0d132db0c65777412fe04','rpy2-2.0.8.win32-py'+python_version_dec+'.msi'],
                        'r11'    : ['http://cran.r-project.org/bin/windows/base/old/2.11.1/R-2.11.1-win32.exe', 'R-2.11.1-win32.exe'],
                        'r12'    : ['http://cran.r-project.org/bin/windows/base/old/2.12.1/R-2.12.1-win.exe', 'R-2.12.1-win32.exe'],
                        'fw_tools' : ['http://home.gdal.org/fwtools/FWTools247.exe', 'FWTools247.exe'],
                        'numexpr' :['https://code.google.com/p/numexpr/downloads/detail?name=numexpr-1.4.2.win32-py'+python_version_dec+'.exe&can=2&q=','numexpr-1.4.2.win32-py'+python_version_dec+'.exe'],
                        'matplotlib' : ['http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.1.1/matplotlib-1.1.1.win32-py'+python_version_dec+'.exe/download', 'matplotlib-1.1.1rc.win32-py2.6.exe'],
                        'scipy' : ['http://sourceforge.net/projects/scipy/files/scipy/0.10.1/scipy-0.10.1-win32-superpack-python'+python_version_dec+'.exe', 'scipy-0.10.1-win32-superpack-python'+python_version_dec+'.exe'],
                        'gdalwin32':['http://download.osgeo.org/gdal/win32/1.6/gdalwin32exe160.zip', 'ggdalwin32exe160.zip'],
                        'pywin32' : ['http://sourceforge.net/projects/pywin32/files/pywin32/Build%20217/pywin32-217.win32-py'+python_version_dec+'.exe','pywin32-217.win32-py'+python_version_dec+'.exe'],
                        'pil' : ['http://effbot.org/downloads/PIL-1.1.7.win32-py'+python_version_dec+'.exe', 'PIL-1.1.7.win32-py'+python_version_dec+'.exe'],
                        'basemap' : ['http://sourceforge.net/projects/matplotlib/files/matplotlib-toolkits/basemap-1.0.5/basemap-1.0.5.win32-py'+python_version_dec+'.exe', 'basemap-1.0.5.win32-py'+python_version_dec+'.exe']
                        }
    #extensions = {'dbfpy':'.exe','numpy': '.exe','gdal' : '.exe','rpy2' : '.msi'}
    #Finds the url and .exe name from the install_packages dictionary
    url = install_packages[package_name][0]
    exe = cwd + '/'+install_packages[package_name][1]

    #Downloads the executable
    if os.path.exists(exe) == False:
        print 'Downloading', os.path.basename(exe)
        File = urllib.urlretrieve(url, exe)

    #If it's not a zip file, it tries to run it, first as a .exe, and then as .msi
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
        smart_unzip(exe)

    if cleanup == True:
        try:
            os.remove(exe)
        except:
            print 'Could not remove:', os.path.basename(exe)
################################################################
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

#########################################################################
##
##try:
##
##    path = os.environ.get('PATH')
##    if path[-1] != ';':
##        path += ';'
##
##    path = path + gdal_bin_dir
##    print path
##    os.putenv('GDAL_DATA', gdal_data_dir)
##    os.putenv('PATH',path)
##    print os.environ.get('GDAL_DATA')
##    os.chdir('c:\\windows\\system32')
##    from osgeo import gdal
##    from osgeo import gdal_array
##    from osgeo import osr, ogr
##    from osgeo import gdalconst
##    os.chdir(cwd)
##
##except:
##
##    admin = tkMessageBox.askyesno('Administrator','Are you an administrator?')
##    if admin:
## #       install('gdalwin32')
##        install('gdal')
##        install('pywin32')
##        install('numpy')
##        path = os.environ.get('PATH')
##        if path[-1] != ';':
##            path += ';'
##
##        path = path + python_dir+'\\Lib\\site-packages\\gdalwin32-1.6\\bin'
##        os.putenv('GDAL_DATA',python_dir+'\\Lib\\site-packages\\gdalwin32-1.6\\data')
##        os.putenv('PATH',path)
##
##        try:
##            from osgeo import gdal
##            from osgeo import gdal_array
##            from osgeo import osr, ogr
##        except:
##            print 'Installation of gdal/osgeo was unsuccessful'
##            print 'Please search for GDAL-1.6.1.win32-py'+python_version_dec+'.exe and manually install'
##            raw_input('Press enter to exit')
##            sys.exit()
##    else:
##        tkMessageBox.showinfo('Administrator','You must be administrator to install the software.')
##        sys.exit()
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

##################################################################
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
if needs_r:
    try:
        os.chdir(program_files_dir + '/R/R-2.11.1/bin')
        path = os.getenv('PATH')
        if path[-1] != ';':
            path += ';'
        r_home = program_files_dir.replace('/', '\\') + 'R\\R-2.11.1'
        win32com_path = python_dir + '\\Lib\\site-packages\\win32'
        sys.path.append(win32com_path)
        path = path + r_home
        os.putenv('PATH',path)
        os.putenv('R_HOME',r_home)
        #os.putenv('Rlib',os.path.split(r_home)[0] + '\\library')
        print 'r_home:',r_home
        print os.getenv('R_HOME')

        import rpy2.robjects as RO
        import rpy2.robjects.numpy2ri
        r = RO.r
        os.chdir(cwd)
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


    ################################################################
    try:
        print 'Importing rscript'
        from Rscript import *

    ##    r_dir = program_files_dir + 'R/R-2.12.1/bin/'
    ##    if os.path.exists(r_dir) == False:
    ##        warning = showwarning('!!!MUST READ!!!!', 'In the "Select Additional Tasks" window, ensure that the "Save version number in registry" option is unchecked\n'\
    ##                              'The script will not run properly if left checked')
    ##        r1 = R()
    ##        r1 = None
    except:
        print 'Cannot use Rscript module'
################################################################
def check_zero_start(in_number,break_numbers = [100,10]):
    ns = str(in_number)
    for bn in break_numbers:
        if float(in_number) < bn:
            ns = '0' + ns
    return ns
def possible_compositing_periods(period_length = 8):
    ocps = []
    just_starts = []
    cps = range(1,365,period_length)
    for cp in cps:
        cps1 = check_zero_start(cp,[100,10])
        cps2 = check_zero_start(cp + 15,[100,10])
        ocps.append([cps1,cps2])
        just_starts.append(cps1)
    return ocps, just_starts
def now(Format = "%b %d %Y %H:%M:%S %a"):
    import datetime
    today = datetime.datetime.today()
    s = today.strftime(Format)
    d = datetime.datetime.strptime(s, Format)
    return d.strftime(Format)
def date_modified(File):
    import datetime
    #return time.ctime(os.path.getmtime(File))
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(File)
    return mtime, datetime.datetime.strptime(time.ctime(ctime), '%a %b %d %H:%M:%S %Y')

def year_month_day_to_seconds(year_month_day):
    import datetime, calendar
    ymd = year_month_day
    return calendar.timegm(datetime.datetime(ymd[0], ymd[1], ymd[2]).timetuple())
#######################################
################################################################
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
################################################################
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
############################################################################################
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
def collapse(in_list):
    out_list = []
    for i in in_list:
        if type(i) == list:

            for i2 in i:
                out_list.append(i2)
        else:
            out_list.append(i)
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
########################################################################################
#Function to convert a specified column from a specified dbf file into a list
#e.g. dbf_to_list(some_dbf_file, integer_column_number)
def dbf_to_list(dbf_file, field_name):

    if os.path.splitext(dbf_file)[1] == '.shp':
        dbf_file = os.path.splitext(dbf_file)[0] + '.dbf'
    #The next exception that is handled is handled within an if loop
    #This exception would occur if a non .dbf file was entered
    #First it finds wither the extension is not a .dbf by splitting the extension out
    if os.path.splitext(dbf_file)[1] != '.dbf':
        #Then the user is prompted with what occured and prompted to exit as above
        print 'Must input a .dbf file'
        print 'Cannot compile ' + dbf_file
        raw_input('Press enter to continue')
        sys.exit()

    #Finally- the actual function code body
    #First the dbf file is read in using the dbfpy Dbf function
    db = dbf.Dbf(dbf_file)
    #Db is now a dbf object within the dbfpy class

    #Next find out how long the dbf is
    rows = len(db)

    #Set up a list variable to write the column numbers to
    out_list = []

    #Iterate through each row within the dbf
    for row in range(rows):
        print row
        #Add each number in the specified column number to the list
        out_list.append(db[row][field_name])
    db.close()
    #Return the list
    #This makes the entire function equal to the out_list
    return out_list
################################################################
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
def batch_utm_to_geog(zone, coord_list):
    out_list = []
    for coords in coord_list:
        lat, lon =  utm_to_geog(zone, coords[0], coords[1])
        out_list.append([lon, lat])
    return out_list
##############################################################################################
#Converts between Numpy and GDAL data types
#Will automatically figure out which direction it must go (numpy to gdal or gdal to numpy)
def dt_converter(dt):
    Dict = {'u1': 'Byte', 'uint8' : 'Byte', 'uint16': 'UInt16','u2': 'UInt16', 'u4': 'UInt32', 'i2' : 'Int16','i4':'Int32', 'int16':'Int16', 'Float32' : 'float32','float32' : 'Float32', 'Float64' : 'float64','float64' : 'Float64'}
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
    #epsg = spatialRef.Export
    return {'proj4' : proj4, 'wkt': wkt, 'spatialRef' : spatialRef}
def reverseDictionary(Dict):
    return dict(map(lambda a:[a[1], a[0]], Dict.iteritems()))

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
def shape_info(shapefile, runr = False, small = False):
##    r('library(maptools)')
##    r('shp = readShapeSpatial("' + shapefile + '")')
##    r('bbox = data.frame((summary(shp)[2]))')
##    bbox = r('bbox')
##    r('print(summary(shp))')
    ext =os.path.splitext(shapefile)[1]
    if ext != '.shp' and ext in formats_dict.keys():
        return raster_info(shapefile)
    elif ext != '.shp':
        shapefile = os.path.splitext(shapefile)[0] + '.shp'
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


    if small == False:
        projections = projection_format_converter(str(ESRI_projection), 'Wkt')

    shp = None
    lyr = None
    info = {'esri' : projection, 'width': width, 'height': height,'gdal_coords': gdal_coords, 'coords' : coords, 'feature_count': numFeatures, 'zone':zone, 'datum': datum, 'crs':crs, 'projection': projection}
    if small == False:
        info['proj4'] = projections['proj4']
        info['wkt'] = projections['wkt']
    return info
##############################################################################################
def xy_list_to_kml(xy_list, kml, zone = '', utm_or_geog = 'utm', lonIndex = 0, latIndex = 1):
    ID = os.path.basename(kml)
    out_kml = '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document id="'+ID+'">\n<name>'+ID+'</name>\n'
    out_kml += '<Snippet></Snippet>\n<Folder id="FeatureLayer0">\n<name>'+ID+'</name>\n<Snippet></Snippet>\n'
    kml = os.path.splitext(kml)[0] + '.kml'

    i = 1
    for line in xy_list:
        x = line[lonIndex]
        y = line[latIndex]

        if utm_or_geog == 'utm':
            coords = utm_to_geog(zone, x, y)
        else:
            coords = [x, y]

        out_kml += '<Placemark>\n<name>'+str(i)+'</name>\n<styleUrl>#IconStyle00</styleUrl>\n<Snippet></Snippet>\n<Point>\n<extrude>0</extrude>\t<altitudeMode>relativeToGround</altitudeMode>\n'

        out_kml += '<coordinates> '+str(coords[0])+','+str(coords[1])+',0.000000</coordinates>\n</Point>\n</Placemark>\n'
        i += 1

    out_kml += '</Folder>\n<Style id="IconStyle00">\n<IconStyle>\n<Icon><href>http://www.google.com/intl/en_us/mapfiles/ms/icons/red-dot.png</href></Icon>\n<scale>1.000000</scale>\n</IconStyle>\n<LabelStyle>\n<color>00000000</color>\n<scale>0.000000</scale>\n</LabelStyle>\n</Style>\n</Document>\n</kml>'

    out_open = open(kml, 'w')
    out_open.writelines(out_kml)
    out_open.close()

##############################################################################################
#Converts a CSV to kml
def csv_to_kml(csv, kml, zone = '', utm_or_geog = 'utm',header = True,id = False,iconURL = 'http://maps.google.com/mapfiles/kml/shapes/cross-hairs_highlight.png'):
    open_csv = open(csv, 'r')
    lines = open_csv.readlines()
    open_csv.close()
    print(lines)
    ID = os.path.basename(csv)

    out_kml = '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document id="'+ID+'">\n<name>'+ID+'</name>\n'
    out_kml += '<Snippet></Snippet>\n<Folder id="FeatureLayer0">\n<name>'+ID+'</name>\n<Snippet></Snippet>\n'
    out_kml += '<Style id="pushpin">\n<IconStyle id="mystyle">\n<Icon>\n<href>'+iconURL+'</href>\n'
    out_kml +='<scale>1.0</scale>\n</Icon>\n</IconStyle>\n</Style>\n'
    if header == True:
        lines = lines[1:]
    if id:
        xIndex = 1
        yIndex = 2
    else:
        xIndex = 0
        yIndex = 1
    i = 1
    for line in lines:
        x = float(line.split(',')[xIndex])
        y = float(line.split(',')[yIndex][:-1])
        print(x,y)
        if id:
            idNo =line.split(',')[0]
        else:
            idNo  = i
        if utm_or_geog == 'utm':
            coords = utm_to_geog(zone, x, y)
        else:
            coords = [x, y]

        out_kml += '<Placemark>\n<name>'+str(idNo)+'</name>\n<styleUrl>#pushpin</styleUrl>\n<Snippet></Snippet>\n<Point>\n<extrude>0</extrude>\t<altitudeMode>relativeToGround</altitudeMode>\n'
        out_kml += '<coordinates> '+str(coords[1])+','+str(coords[0])+',0.000000</coordinates>\n</Point>\n</Placemark>\n'
        i += 1

    out_kml += '</Folder>\n<Style id="IconStyle00">\n<IconStyle>\n<Icon><href>000000.png</href></Icon>\n<scale>1.000000</scale>\n</IconStyle>\n<LabelStyle>\n<color>00000000</color>\n<scale>0.000000</scale>\n</LabelStyle>\n</Style>\n</Document>\n</kml>'

    out_open = open(kml, 'w')
    out_open.writelines(out_kml)
    out_open.close()
##############################################################################################
def shape_to_kml(in_shp, out_kml, name_field = 'NAME',gdal_dir = program_files_dir + '/FWTools2.4.7/bin/'):
    #print 'Converting', base(in_shp),'to',base(out_kml)
    gdal_call = gdal_dir + 'ogr2ogr -f KML "' + out_kml + '" "' + in_shp + '" -dsco NameField=' + name_field
    print gdal_call
    call = subprocess.Popen(gdal_call)
    call.wait()

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
def get_xo_yo_w_h(large_coords,small_coords,res):
    large_height =int((large_coords[-1] - large_coords[1])/res)
    large_width =int((large_coords[-2] - large_coords[0])/res)
    xo = int(math.floor((small_coords[0] - large_coords[0])/res))
    yo = int(math.ceil((large_coords[-1] - small_coords[-1])/res))
    if xo < 0:
        xo = 0
    if yo < 0:
        yo = 0
    if xo == 0:
        w = int(math.floor((small_coords[2] - small_coords[0])/res))
    else:
        w = int(math.floor((small_coords[2] - small_coords[0])/res))
    if yo == 0:
        h = int(math.floor((large_coords[-1] - small_coords[1])/res))
    else:
        h = int(math.floor((small_coords[-1] - small_coords[1])/res))

    if h + yo > large_height:
        h = large_height-yo
    if w + xo > large_width:
        w = large_width - xo
    return xo,yo,w,h
def burn_in_raster(small_raster,large_raster,no_data = '',Min = '',Max = ''):
    sri = raster_info(small_raster)
    lri = raster_info(large_raster)
    s_res,s_coords = sri['res'],sri['coords']
    l_res, l_coords = lri['res'],lri['coords']

    xo,yo,w,h = get_xo_yo_w_h(l_coords,s_coords,s_res)
    rs = brick(small_raster)
    if Max != '':
        print 'Applying max'
        rs[rs > Max] = Max
    if Min != '':
        print 'Applying min'
        rs[rs < Min] = Min
    #yo = yo +1
    update_raster(large_raster,rs,xo,yo,no_data)

##############################################################################################
#Updates values of an existing raster with an input array
#If image is multi-band and array is single band, the single band will be applied across all input image bands
#No data values in the array will not be updated
def update_raster(image_to_update, array,xo,yo, no_data = ''):
    rast = gdal.Open(image_to_update, gdal.GA_Update)

##    if no_data != '' and no_data != None:
##        print 'Masking no data value:', no_data
##        array = numpy.ma.masked_equal(array, int(no_data))
    ri= raster_info(image_to_update)
    ri_dt = ri['dt']
    if numpy_or_gdal(ri_dt) == 'gdal':

        numpy_dt = dt_converter(ri_dt)
    else:
        numpy_dt = ri_dt
    array = numpy.array(array).astype(numpy_dt)
    no_image_bands = ri['bands']
    if array.ndim == 2:
        no_array_bands = 1

    elif array.ndim == 3:
        no_array_bands = len(array)
    a_width = array.shape[-1]
    a_height = array.shape[-2]
    for i in range(no_image_bands):
        print 'Updating band:', i + 1
        br = rast.GetRasterBand(i + 1)

        if array.ndim == 3:
            at = array[i]
            if no_data != '' and no_data != None:
                print 'Masking no data value:', no_data
                print 'Numpy dt:', numpy_dt
                from_array = br.ReadAsArray(xo, yo, a_width, a_height).astype(numpy_dt)
                msk = numpy.equal(at,no_data)
                print 'msk',msk
                print 'msk_shp',msk.shape
                print 'at_shp', at.shape
                print 'from_array_shp', from_array.shape
                numpy.putmask(at,msk,from_array)
                print at
##                from_array[at != no_data] = 0
##                at[at == no_data ] = 0
##                at = numpy.amax([from_array,at], axis = 0)
            br.WriteArray(at,xo,yo)
        else:
            if no_data != '' and no_data != None:
                print 'Masking no data value:', no_data
                print 'Numpy dt:', numpy_dt
                from_array = br.ReadAsArray(xo, yo, a_width, a_height).astype(numpy_dt)
                msk = numpy.equal(array,no_data)
                print 'msk',msk
                numpy.putmask(array,msk,from_array)
                #from_array[array != no_data] = 0
                #array[array == no_data ] = 0
                #array = numpy.amax([from_array,array], axis = 0)
            br.WriteArray(array,xo,yo)
    brick_info(image_to_update, get_stats = True)
    rast = None
##############################################################################################

def update_color_table_or_names(image,color_table = '',names = ''):
    rast = gdal.Open(image, gdal.GA_Update)
    b = rast.GetRasterBand(1)
    if color_table != '' and color_table != None:
        print 'Updating color table for:',image
        b.SetRasterColorTable(color_table)
    if names != '' and names != None:
        print 'Updating names for:',image
        b.SetRasterCategoryNames(names)
##############################################################################################
def just_raster_extent(raster):
    rast = gdal.Open(raster)
    width = rast.RasterXSize
    height = rast.RasterYSize
    transform = rast.GetGeoTransform()
    rast = None
    transform = list(transform)
    xmax = transform[0] + (int(round(transform[1])) * width)
    xmin = transform[0]
    ymax = transform[3]
    ymin = transform[3]- (int(round(transform[1])) * height)

    return [xmin,ymin,xmax,ymax]
##############################################################################################
#Gathers various information about a raster and returns it in a dictionary
def raster_info(image = '', band_no = 1, get_stats = False, guiable = True):
    if image == '':
        guied = True
        image = str(askopenfilename(title = 'Select Strata Raster',filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))
    else:
        guied = False
    #print image
    rast = gdal.Open(image)
    band1 = rast.GetRasterBand(band_no)
    dt = band1.DataType
    no_data = band1.GetNoDataValue()

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
    try:
        dt_range = dt_ranges[dataType]
    except:
        dt_range = [0,255]

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

    info = {'image':image,'no_data' : no_data, 'proj4': projections['proj4'], 'wkt': projections['wkt'], 'units': units,
            'hemisphere' : hemisphere,'min': Min, 'max': Max, 'mean': mean, 'std':stdev, 'stdev':stdev,
            'gdal_coords': gdal_coords, 'coords' : coords, 'projection':projection, 'transform': transform,
            'width': width, 'height': height, 'bands': bands, 'band_count': bands, 'zone' : zone, 'datum': datum,
            'res': res, 'resolution':res, 'dt_range': dt_range,'datatype': dataType, 'dt': dataType, 'DataType': dataType}
    if guied == True:
        for piece in info:
            print piece, info[piece]
    rast  = None
    return info
#print raster_info(r'D:\Valley_Bottom_Logistic_Model\lidar_output_predictors2\6270_37380_Euclidean_Distance_from_Channel.img')['transform']
##############################################################################################
#Applies raster_info across all bands and returns a list of raster_info dictionaries
def brick_info(image = '', get_stats = False):
    info = []
    map(lambda band : info.append(raster_info(image, band, get_stats)), range(1, raster_info(image)['bands'] + 1))
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
def is_leap_year(year):
    year = int(year)
    if year % 4 == 0:
        if year%100 == 0 and year % 400 != 0:
            return False
        else:
            return True
    else:
        return False
##############################################################################################
def julian_to_calendar(julian_date, year  = time.localtime()[0]):
    julian_date, year = int(julian_date), int(year)
    is_leap = is_leap_year(year)
    if is_leap:
        leap, length = True, [31,29,31,30,31,30,31,31,30,31,30,31]
    else:
        leap, length = False, [31,28,31,30,31,30,31,31,30,31,30,31]
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
def calendar_to_julian(day, month, year = time.localtime()[0]):
    day, month, year = int(day),int(month),int(year)
    is_leap = is_leap_year(year)
    n, nl=[0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334], [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]

    x = 1
    while x <=12:
        if month == x:
            if not is_leap:
                julian = n[x-1]+ day
            else:
                julian = nl[x-1]+ day
            return julian
        x = x+1

##############################################################################################
def base(in_path):
    return os.path.basename(os.path.splitext(in_path)[0])
##############################################################################################
def check_dir(in_path):
    if os.path.exists(in_path) == False:
        print 'Making dir:', in_path
        os.makedirs(in_path)
##############################################################################################
def check_end(in_path, add = '/'):
    if in_path[-len(add):] != add:
        out = in_path + add
    else:
        out = in_path
    return out
##############################################################################################
#Returns all files containing an extension or any of a list of extensions
#Can give a single extension or a list of extensions
def glob(Dir, extension):
    Dir = check_end(Dir)
    if type(extension) != list:
        if extension.find('*') == -1:
            return map(lambda i : Dir + i, filter(lambda i: os.path.splitext(i)[1] == extension, os.listdir(Dir)))
        else:
            return map(lambda i : Dir + i, os.listdir(Dir))
    else:
        out_list = []
        for ext in extension:
            tl = map(lambda i : Dir + i, filter(lambda i: os.path.splitext(i)[1] == ext, os.listdir(Dir)))
            for l in tl:
                out_list.append(l)
        return out_list
##############################################################################################
#Returns all files containing a specified string (Find)
def glob_find(Dir, Find):
    Dir = check_end(Dir)
    if type(Find) != list:
        return map(lambda i : Dir + i, filter(lambda i:i.find(Find) > -1, os.listdir(Dir)))
    else:
        out_list = []
        for F in Find:
            t1 = map(lambda i : Dir + i, filter(lambda i:i.find(F) > -1, os.listdir(Dir)))
            for t in t1:

                out_list.append(t)

        return out_list
##############################################################################################
#Returns all files ending with a specified string (end)
def glob_end(Dir, end):
    Dir = check_end(Dir)
    if type(end) != list:
        return map(lambda i : Dir + i, filter(lambda i:i[-len(end):] == end, os.listdir(Dir)))
    else:
        out_list = []
        for ed in end:
            t1 = map(lambda i : Dir + i, filter(lambda i:i[-len(ed):] == ed, os.listdir(Dir)))
            for t in t1:
                out_list.append(t)
        return out_list
##############################################################################################
##def glob_find_iter(Dir, find_list):
##    out_list = []
##    Find = find_list[0]
##    tl1 = map(lambda i : Dir + i, filter(lambda i:i.find(Find) > -1, os.listdir(Dir)))
##    for Find in find_list[1:]:
##
##
##############################################################################################
def set_no_data(image, no_data_value = -9999, update_stats = True):
    rast = gdal.Open(image, gdal.GA_Update)
    ri = raster_info(image)
    nd = ri['no_data']
    print 'Processing no_data for:',base(image)
    if nd != no_data_value:

        print 'Changing no data from:',nd,'to',no_data_value
        for band in range(1, ri['bands']+1):

            b = rast.GetRasterBand(band)
            b.SetNoDataValue(no_data_value)
            if update_stats:
                print 'Updating stats for band:',band
                Min,Max,Mean,Std = b.ComputeStatistics(0)
                b.SetStatistics(Min,Max,Mean,Std)
            else:
                Min,Max,Mean,Std =  b.GetStatistics(0,0)
            print 'Min:',Min
            print 'Max:',Max
            print 'Mean:',Mean
            print 'Std:', Std
    else:
        print 'No data already = ', no_data_value
    print
##Dir = 'D:/claslite/PNG_Test/'
##tifs = glob(Dir, '.tif')
##for tif in tifs:
##    set_no_data(tif, -32768,True)
def set_stats(image,Min=None,Max=None,Mean=None,Std=None):
    rast = gdal.Open(image, gdal.GA_Update)
    ri = raster_info(image)
    nd = ri['no_data']

    for band in range(1, ri['bands']+1):

        b = rast.GetRasterBand(band)
        b.SetStatistics(Min,Max,Mean,Std)
    #rast = None

def set_projection(image,crs):


    rast = gdal.Open(image, gdal.GA_Update)
    rast.SetProjection(crs)
    rast = None
##
##proj = 'PROJCS["NAD83 / Conus Albers",\
##  GEOGCS["NAD83",\
##    DATUM["North American Datum 1983",\
##      SPHEROID["GRS 1980", 6378137.0, 298.257222101, AUTHORITY["EPSG","7019"]],\
##      TOWGS84[1.0, 1.0, -1.0, 0.0, 0.0, 0.0, 0.0],\
##      AUTHORITY["EPSG","6269"]],\
##    PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]],\
##    UNIT["degree", 0.017453292519943295],\
##    AXIS["Geodetic longitude", EAST],\
##    AXIS["Geodetic latitude", NORTH],\
##    AUTHORITY["EPSG","4269"]],\
##  PROJECTION["Albers Equal Area", AUTHORITY["EPSG","9822"]],\
##  PARAMETER["central_meridian", -96.0],\
##  PARAMETER["latitude_of_origin", 23.0],\
##  PARAMETER["standard_parallel_1", 29.5],\
##  PARAMETER["false_easting", 0.0],\
##  PARAMETER["false_northing", 0.0],\
##  PARAMETER["standard_parallel_2", 45.5],\
##  UNIT["m", 1.0],\
##  AXIS["Easting", EAST],\
##  AXIS["Northing", NORTH],\
##  AUTHORITY["EPSG","5070"]]'
##Dir = 'D:/Downloads/rtfd_baselines/'
##tifs = glob(Dir,'.tif')
##for tif in tifs:
##    set_projection(tif,proj)
##    set_no_data(tif,-32768)
##############################################################################################
def quick_look(tar_list, out_dir, bands = [], leave_extensions = ['_MTLold.txt', '_MTL.txt'], df = 'ENVI', out_extension = ''):
    if os.path.exists(out_dir) == False:
        os.makedirs(out_dir)
    out_dir_temp = out_dir + 'individual_bands/'
    out_dir_not_now = out_dir_temp + 'old_bands/'
    if os.path.exists(out_dir_temp) == False:
        os.makedirs(out_dir_temp)
    if os.path.exists(out_dir_not_now) == False:
        os.makedirs(out_dir_not_now)
    stack_out_list = []
    for tar in tar_list:
        if tar.find('.tar.gz') > -1:
            stack_out = out_dir + os.path.basename(tar.split('.tar.gz')[0]) + out_extension
        else:
            stack_out = out_dir + os.path.splitext(os.path.basename(tar))[0] + out_extension

        stack_out_list.append(stack_out)
        if os.path.exists(stack_out) == False:
            try:
                untar(tar, out_dir_temp, bands = bands)
            except:
                print 'Could not untar all files in', os.path.basename(tar)
            t_files = glob(out_dir_temp, '*')
            tto_stack = glob(out_dir_temp, '.TIF')
            if len(tto_stack) == 0:
                tto_stack = glob(out_dir_temp, '.tif')
            to_stack = [tto_stack[0]]
            res = raster_info(tto_stack[0])['res']

            for to in tto_stack[1:]:
                try:
                    rt = raster_info(to)['res']
                    if rt == res:
                        to_stack.append(to)
                except:
                    print 'Could not include', os.path.basename(to), ' in stack'
            stack(to_stack, stack_out, to_stack[0], df = df)

            for File in t_files:
                not_now_filename = out_dir_not_now + os.path.basename(File)
                if os.path.isdir(File) == False:
                    is_in = 0
                    for extension in leave_extensions:
                        if File.find(extension) > -1:
                            is_in = 1
                    if is_in == 0:
                        if os.path.exists(not_now_filename) == False:
                            try:
                                shutil.move(File, not_now_filename)
                            except:
                                print 'Could not move', File
                        else:
                            try:
                                os.remove(File)
                            except:
                                print 'Could not remove', File
                    else:
                        try:
                            shutil.move(File, out_dir + os.path.basename(File))
                        except:
                            print 'Could not move', File
        else:
            print 'Already created:', stack_out


###############################################################################################Untars Landsat TM (or any) tarball
def untar(tarball, output_dir = '', bands = []):
    if output_dir == '':
        output_dir = os.path.dirname(tarball) + '/'
    out_list = []
    out_folder = os.path.basename(tarball).split('.')[0].split('[')[0]

    if os.path.exists(output_dir + out_folder) == False:

        try:
            tar = TarFile.open(tarball, 'r:gz')
        except:
            tar = TarFile.open(tarball, 'r')
        #tar = gzip.open(tarball)
        if bands == []:
            print 'Unzipping:', os.path.basename(tarball)
            tar.extractall(path = output_dir)
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

#File = 'C:/Users/ihousman/Downloads/rsgislib-2.0.0.tar'
#out_dir = 'C:/Users/ihousman/Downloads/'
#untar(File,out_dir)
#gz = '//166.2.126.38/2013_Composites_Compressed/AQUA/113_128/zone14_path_113_128_AQUA_composite_surface_reflectance.img.gz'
#outfile = 'C:/Users/ihousman/Downloads/' + base(gz)

def ungz(gz, outfile = ''):
    if outfile == '' or outfile == None:
        outfile = os.path.splitext(gz)[0]
    if os.path.exists(outfile) == False:
        print 'Un gzing:', gz
        infile = gzip.open(gz, 'rb')
        output = open(outfile, 'wb')

        file_content = infile.read()
        output.writelines(file_content)
        output.close()

    else:
        print 'Already created:', outfile
##############################################################################################
#Will read a raster into a numpy array
#Returns a numpy array
#u1,u2,u4, i1,i2,i4, float32, float64
#Does not support < unsigned 8 byte
def raster(Raster, dt = '', band_no = 1, xoffset = 0, yoffset = 0, width = '', height = '', na_value = ''):
    #os.chdir('C:/Python26/ArcGIS10.0/Lib/site-packages/osgeo')
    info = raster_info(Raster)
    if dt == '':
        dt = info['dt']
    if numpy_or_gdal(dt) == 'gdal':

        dt = dt_converter(dt)
    if width == '':
        width = info['width'] - xoffset
    if height == '':
        height = info['height']- yoffset
    band_no = int(band_no)
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
    if na_value != '':
        band1_pixels = numpy.ma.masked_equal(band1_pixels, int(na_value))
    return band1_pixels
    band1_pixels = None
def brick(Raster, dt = '', xoffset = 0, yoffset = 0, width = '', height = '', band_list = [], na_value = '', image_list = False):
    if image_list == True:
        band_list = range(1, len(Raster) + 1)
        info = raster_info(Raster[0])
    else:
        info = raster_info(Raster)
    if band_list != [] and band_list != '' and band_list != None:
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
    try:
        print 'Reading raster:', Raster.split('/')[-1]
    except:
        print 'Reading raster'
    print 'Datatype:',dt


    array_list = numpy.zeros([len(bands), height, width], dtype = dt)
    if image_list == False:
        rast = gdal.Open(Raster)
        array_no = 0
        for band in bands:
            print 'Reading band number:', band
            band1 = rast.GetRasterBand(band)

            band1_pixels = band1.ReadAsArray(xoffset, yoffset, width, height).astype(dt)

            array_list[array_no] = band1_pixels
            array_no += 1

    else:
        array_no = 0
        for raster in Raster:
            rast = gdal.Open(raster)
            print 'Reading:', os.path.basename(raster)
            band1 = rast.GetRasterBand(1)
            band1_pixels = band1.ReadAsArray(xoffset, yoffset, width, height).astype(dt)
            array_list[array_no] = band1_pixels
            array_no += 1
    rast = None
    band1 = None
    band1_pixels = None
    print 'Returning', len(array_list),'band 3-d array'
    array_list = numpy.array(array_list)
    if na_value != '' and na_value != None:
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
######################################################################################
#Function intended to be used to divide a list into threads
#Returns a 2-d array of lists of parts of the list for each thread
def set_maker(in_list, threads):
    out_sets = []
    tl = len(in_list) / threads
    remainder = len(in_list) % threads
    i = 0
    for t in range(threads):
        tt = []
        while len(tt) < tl:
            tt.append(in_list[i])
            i += 1
        out_sets.append(tt)

    for r in range(remainder):
        out_sets[r].append(in_list[i])
        i += 1
    #print 'The sets are', out_sets
    return out_sets
######################################################################################
def new_set_maker(in_list,threads):

    out_sets =[]
    for t in range(threads):
        out_sets.append([])
    i =0
    for il in in_list:

        out_sets[i].append(il)
        i += 1
        if i >= threads:
            i = 0
    return out_sets
######################################################################################
#Function intended to be used to call on a batch file externally
#Generally used as part of multi-threading
def bat_thread(bat_lines, bat_name, run = True):
    blno = open(bat_name, 'w')
    blno.writelines(bat_lines)
    blno.close()

    if run == True:
        call = subprocess.Popen(bat_name)
        call.wait()
###########################################################################################
#Function intended to be used to call on a Python script externally
#Generally used as part of multi-threading
def python_thread(script_lines, script_name, run = True):
    sco = open(script_name, 'w')
    sco.writelines(script_lines)
    sco.close()
    bl = []
    bl.append('cd\\ \n')
    bl.append(script_name[:2] + '\n')
    #bl.append('cd ' + os.path.dirname(script_name) + '\n')
    #bl.append(os.path.basename(script_name) + '\n')
    bl.append(script_name + '\n')
    bln = script_name + '.bat'
    blno = open(bln, 'w')
    blno.writelines(bl)
    blno.close()

    if run == True:
        call = subprocess.Popen(bln)
        call.wait()
###########################################################################################
def r_thread(script_lines, script_name, r_bin_dir, run = True):
    sco = open(script_name, 'w')
    sco.writelines(script_lines)
    sco.close()
    bl = []
    bl.append('cd\\ \n')
    #bl.append(script_name[:2] + '\n')
    bl.append('cd ' + r_bin_dir + '\n')
    bl.append('"' + r_bin_dir + 'rscript.exe" "' + script_name+ '"\n')
    bln = script_name + '.bat'
    blno = open(bln, 'w')
    blno.writelines(bl)
    blno.close()

    if run == True:
        call = subprocess.Popen(bln)
        call.wait()
###########################################################################################
def reset_no_data(in_image, out_image, in_no_data = -9999, out_no_data = 0):
    if os.path.exists(out_image) == False:
        print 'Creating', out_image
        ti = tiled_image(out_image, in_image, outline_tiles = True, out_no_data = out_no_data)
        ci = 1
        for xo,yo,w,h in ti.chunk_list:
            print 'Recoding chunk', ci, 'out of', len(ti.chunk_list)
            r = brick(in_image, '',xo,yo,w,h)
            print 'Recoding', in_no_data,'to', out_no_data
            r[r == in_no_data] = out_no_data

            ti.add_tile(r, xo,yo)
            r = None
            ci +=1

        ti.rm()
        ti = None
        print 'Computing stats for', out_image
        raster_info(out_image, get_stats = True)
######################################################################################
def check_xy(x,y):
    if x == '':
        x = numpy.arange(1, len(y) + 1)
    elif y == '':
        y = numpy.arange(1, len(x) + 1)
    x = numpy.array(x).astype('Float32')
    y = numpy.array(y).astype('Float32')
    return x,y
def rmse(actual,predicted):
    error = actual - predicted
    return numpy.sqrt(numpy.mean(error**2))
def mae(actual, predicted):
    error = actual - predicted
    return  numpy.mean(numpy.absolute(error))
def rmse_mae(actual,predicted):
    error = actual - predicted
    return numpy.sqrt(numpy.mean(error**2)), numpy.mean(numpy.absolute(error))
def r_value(n,sum_x,sum_y, sum_xy, sum_x2,sum_y2):
    return ((n * sum_xy) - (sum_x* sum_y))/((((n * sum_x2) - (sum_x * sum_x))**0.5)*((n * sum_y2) - sum_y**2)**0.5)
def quick_linregress(x = '', y = '', only_slope = False, only_slope_r = False):

    x,y = check_xy(x,y)

    xy = x*y
    x2 = x * x
    y2 = y*y
    sum_x = numpy.sum(x)

    sum_y = numpy.sum(y)
    sum_xy = numpy.sum(xy)
    sum_x2 = numpy.sum(x2)
    sum_y2 = numpy.sum(y2)
    n = float(len(x))
    slope = ((n * sum_xy) - (sum_x * sum_y))/((n * sum_x2) - (sum_x* sum_x))

    if only_slope:
        return slope
    elif only_slope_r:
        r =r_value(n,sum_x,sum_y,sum_xy, sum_x2, sum_y2)
        return slope, r
    else:
        intercept = (sum_y - (slope * sum_x))/ n
        y_pred = slope*x + intercept
        #error = y - y_pred
        rmse_out, mae_out = rmse_mae(y,y_pred)
        r =r_value(n,sum_x,sum_y,sum_xy, sum_x2, sum_y2)
        return slope, intercept,r, rmse_out, mae_out
##import numexpr
##def tsum(in_array):
##    return numpy.sum(in_array)
def quick_linregress_numexpr(x = '', y = '', only_slope = False, only_slope_r = False):

    x,y = check_xy(x,y)

    xy = x*y
##    x2 = x * x
##    y2 = y*y
##    sum_x = numpy.sum(x)
##
##    sum_y = numpy.sum(y)
    sum_xy = numpy.sum(xy)
##    sum_x2 = numpy.sum(x2)
##    sum_y2 = numpy.sum(y2)
    n = float(len(x))
    slope = numexpr.evaluate('((n *tsum(x)))')# - (sum(x) * sum(y)))')#/((n * sum(x**2)) - (sum(x)**2))')

    if only_slope:
        return slope
##    elif only_slope_r:
##        r =r_value(n,sum_x,sum_y,sum_xy, sum_x2, sum_y2)
##        return slope, r
##    else:
##        intercept = (sum_y - (slope * sum_x))/ n
##        y_pred = slope*x + intercept
##        #error = y - y_pred
##        rmse_out, mae_out = rmse_mae(y,y_pred)
##        r =r_value(n,sum_x,sum_y,sum_xy, sum_x2, sum_y2)
##        return slope, intercept,r, rmse_out, mae_out
##x = numpy.array(numpy.random.sample(5000000))
##t1 = time.time()
##print quick_linregress(x,'',True)
##t2 = time.time()
##print t2-t1
##t1 = time.time()
##print quick_linregress_numexpr(x,'',True)
##t2 = time.time()
##print t2-t1

def log_transform_lin_regress(x = '',y = '', only_slope = False):
    x,y = check_xy(x,y)
    y = numpy.log10(y)
    return quick_linregress(x,y, only_slope)
def quick_linear_slope(x = '', y = ''):
    out = [quick_linregress(x,y,True)]
    return out
def quick_slope_r(x = '', y = ''):
    return quick_linregress(x,y, False, True)

def poly_fit(x,y, order = 3, rmse_only = False):
    coeffs, others = numpy.polynomial.polynomial.polyfit(x,y,order, full = True)
    rmse = numpy.sqrt(others[0]/len(x))
    if rmse_only == False:
        out = [rmse]
        for coeff in coeffs:
            out.append(coeff)
        return out
    else:
        return rmse
def rmse_poly_fit(x,y, order = 3):
    coeffs, others = numpy.polynomial.polynomial.polyfit(x,y,order, full = True)
    rmse = numpy.sqrt(others[0]/len(x))
    return rmse


#Polynomials
def first_order_poly(x,a,b):
    return a + b*x
def second_order_poly(x, a,b,c):
    return a*x**2 + b*x + c
def third_order_poly(x,a,b,c,d):
    return a*x**3 + b*x**2 + c*x + d
def fourth_order_poly(x,a,b,c,d,f):
    return a*x**4 +b*x**3 + c*x**2 + d*x +f
def fifth_order_poly(x,a,b,c,d,f,g):
    return a*x**5 + b*x**4 + c*x**3 + d*x**2 + f*x +g
def marc_plante_quadratic(x,a,b,c):
    return ((-b + (b**2 - (4*a*(c-x)))**0.5)/2)/a

#Fourier Series
def one_term_scaled_2d(x,a0,a1,b1,c1):
    return a0 + (a1 * scipy.sin(c1 *x)) + (b1 * scipy.cos(c1*x))
def one_term_standard_2d(x,a0,a1,b1):
    return a0 + (a1 * scipy.sin(x)) + (b1 * scipy.cos(x))

def two_term_standard_2d(x,a0,a1,a2,b1,b2):
    return a0 + (a1 * scipy.sin(x)) + (b1 * scipy.cos(x)) + (a2 * scipy.sin(2*x)) + (b2 * scipy.cos(2*x))
def three_term_standard_2d(x,a0,a1,a2,a3,b1,b2,b3):
    return a0 + (a1 * scipy.sin(x)) + (b1 * scipy.cos(x)) + (a2 * scipy.sin(2*x)) + (b2 * scipy.cos(2*x)) + (a3 * scipy.sin(3*x)) + (b3 * scipy.cos(3*x))

#Exponential
def asymptotic_exponential(x,a):
    return 1.0 - (a ** x)
def rmse_mae(actual,predicted):
    error = actual - predicted
    return numpy.sqrt(numpy.mean(error**2)), numpy.mean(numpy.absolute(error))

#Logarithmic
def log_2d_b10(x,a,b):
    return a + (b * scipy.log10(x))

def poly_fit(x,y, order = 3, rmse_only = False):
    coeffs, others = numpy.polynomial.polynomial.polyfit(x,y,order, full = True)
    rmse = numpy.sqrt(others[0]/len(x))
    if rmse_only == False:
        out = [rmse]
        for coeff in coeffs:
            out.append(coeff)
        return out
    else:
        return rmse

def NIST(x, a,b,c,d):
    return (a * (x**2 + (b*x))) /(x**2 +(c*x) + d)

def bioscience(x,a,b,c,d):
    return b + ((a-b)/ (1 + 10**(d *(x-c))))

def burkard(x,a,b,c,d):
    return c * numpy.exp(- numpy.exp(-((x-a)/b))) + d


def test_fit(x,y, function_name = first_order_poly, return_error = True, return_predictions = True,return_coeffs = False):
    x = numpy.array(x)
    y = numpy.array(y)
    try:
        coeffs,cov = curve_fit(function_name, x,y)

        if type(function_name) == str:
            function_name = eval(function_name)
        y_pred = function_name(x, *coeffs)
        rmse_out,mae_out = rmse_mae(y,y_pred)
        return rmse_out,mae_out, y_pred
    except:
        return 0,0,y
def predict(model,x,x_term):
    x_terms = x_term.split(',')
    call = 'predicted = '
    if len(model) == len(x_terms) + 1:
        for i in range(len(x_terms)):
            exec('t = ' + x_terms[i])
            exec('print model['+str(i) + ']')
            print t
            call += 'numpy.dot('+x_terms[i] + ',  model['+str(i) + ']) + '
        call += 'model[' + str(i +1) + ']'
        print call

        exec(call)

        #print predicted
################################################################################################################
def matrix_linregress(y,x = '', vertical_view = False, return_residuals = True, compute_r2 = True, x_term = 'x',in_no_data = '',out_no_data = ''):
    yos = y.shape


    if (in_no_data != None and in_no_data != '') and (out_no_data == None or out_no_data == ''):
        out_no_data = in_no_data

    msk = y[0]

    if x == '' or x == None:
        x = numpy.arange(y.shape[0])
    else:
        x = numpy.array(x)
    n = len(x)
    exec('x =numpy.c_['+x_term+', numpy.ones_like(x)]')

    if vertical_view == False:
        y = numpy.vstack(y.T.swapaxes(1,0)).T
    else:
        y = numpy.array(y)

    print x.shape
    print y.shape




    print 'Computing linear algebra least squares'
    model,residual = numpy.array(numpy.linalg.lstsq(x, y))[:2]



    out = []
    for m in model:
        out.append(m)
    model = None
    if return_residuals and residual != []:
        out.append(residual)

    if compute_r2:
        denom =(y.shape[0] * numpy.var(y,0))
        ratio = residual/denom
        r2 =   1- ratio
        r2[r2 > 1] = 1
        r2[r2 < 0] = 0

        if r2 != []:
            out.append(r2)
        r2 = None
    residual = None
    x = None
    y = None

    out = numpy.array(out).reshape((len(out),yos[1],yos[2]))

    if in_no_data != '' and in_no_data != None:
        for i in range(len(out)):
            print 'Masking layer', i + 1
            out[i][msk == in_no_data] = out_no_data
    msk = None

    return out


#y = numpy.random.random(100).reshape((25,2,2))
##print y
###s,r = quick_slope_r('',y)
###print s,r**2
###y = numpy.random.randint((100).reshape((25,2,2))
##
#print  matrix_linregress(y, x_term = 'x', compute_r2 = True,return_residuals = False)#,in_no_data = y[0][0][0], out_no_data = 501)
def new_big_image_matrix_linregress(in_image,out_image, years = '', in_no_data = 255,out_no_data = -600, mem_size_limit = 20000, layer_names = ['slope', 'b', 'r2'], band_list = []):
    ri = raster_info(in_image)
    log_file = os.path.splitext(out_image)[0] + '_matrix_linregress_log.txt'

    lo = open(log_file, 'a+')
    existing_lines = lo.readlines()
    if existing_lines == []:
        lo.write('Matrix Linear Regression Log\n')
    lo.write('\nFunction:\tnew_big_image_matrix_linregress\nInput image:\t' + in_image + '\nOutput image: ' + out_image + '\nStarted:' + now()+ '\n')
    lo.close()
    if os.path.exists(out_image)== False:
        tb1 = time.time()
        ti= tiled_image(out_image,in_image,bands = 3,dt = 'Float32', size_limit_kb = mem_size_limit, outline_tiles = True, out_no_data = out_no_data)
        i = 1

        lo = open(log_file, 'a+')
        lo.write('Chunk size (mb): ' + str(mem_size_limit) + '\nNumber of chunks to process: ' + str(len(ti.chunk_list))+ '\nBand list: '+str(band_list)+'\nYear list: '+str(years)+'\n')
        for xo,yo,w,h in ti.chunk_list:
            tt1 = time.time()
            lo = open(log_file, 'a+')
            print 'Processing tile:',i,'/', len(ti.chunk_list)
            lo.write('Start\tProcess chunk\t' + str(i) + '\t' + now()+'\n')
            try:
                b = brick(in_image,'Float32', xo,yo,w,h, band_list = band_list)#, na_value = ri['no_data'])
                lo.write('Success\tRead chunk\t' + str(i)+'\t'+now()+'\n')
            except:
                lo.write('Fail\tRead chunk\t' + str(i)+'\t'+now()+'\n')
            try:
                out = matrix_linregress(b,years, vertical_view = False, return_residuals = False, compute_r2 = True, x_term = 'x',in_no_data = ri['no_data'],out_no_data = out_no_data)
                lo.write('Success\tApplied matrix_linregress to chunk\t' + str(i)+'\t'+now()+'\n')
            except:
                lo.write('Fail\tApply matrix_linregress to chunk\t' + str(i)+'\t'+now()+'\n')
            try:
                ti.add_tile(out,xo,yo)
                lo.write('Success\tWrite fit chunk\t' + str(i)+'\t'+now()+'\n')
            except:
                lo.write('Fail\tWrite fit chunk\t' + str(i)+'\t'+now()+'\n')
            tt2 = time.time()
            lo.write('Processing time (sec) chunk\t'+str(i)+'\t'+str(tt2-tt1)+'\n\n')
            lo.close()
            i += 1
        lo = open(log_file, 'a+')
        try:
            ti.rm()
            lo.write('Success\tClose output\t' + out_image+'\t'+now()+'\n')
        except:
            lo.write('Fail\tClose output\t' + out_image+'\t'+now()+'\n')
        try:
            print 'Computing stats for:',out_image
            brick_info(out_image,True)
            lo.write('Success\tCompute Stats\t' + out_image+'\t'+now()+'\n')
        except:
            lo.write('Fail\tCompute Stats\t' + out_image+'\t'+now()+'\n')
        tb2 = time.time()
        lo.write('Processing time (sec):\t'+str(tb2 - tb1)+'\n')
        lo.write('\n\n')
        lo.close()
    else:
        lo = open(log_file, 'a+')
        lo.write('Output image already exists:\t' +out_image + '\t' + now()+ '\n')
        lo.write('\n\n')
        lo.close()


    li = 1
    for layer_name in layer_names:
        ut1 = time.time()
        lo = open(log_file, 'a+')
        out = os.path.splitext(out_image)[0] + '_' + layer_name + '.img'
        if os.path.exists(out) == False:
            try:
                print 'Unstacking', out
                restack(out_image,out,out_image,[li],out_no_data = out_no_data)
                lo.write('Success\tUnstacking\t' + out +'\t'+now()+ '\n')
            except:
                lo.write('Fail\tUnstacking\t' + out + '\t'+now()+ '\n')
            try:
                print 'Computing stats for:', out
                brick_info(out,True)
                lo.write('Success\tCompute Stats\t' + out+'\t'+now()+'\n')
            except:
                lo.write('Fail\tCompute Stats\t' + out+'\t'+now()+'\n')
            ut2 = time.time()
            lo.write('Unstack time\t' + str(ut2-ut1) + '\n\n')

        lo.close()
        li += 1
    lo = open(log_file, 'a+')
    lo.write('Finished processing: ' + now()+'\n\n')
    lo.close()
#####################################################################################################################
def best_function(x,y, function_list = ['first_order_poly',
                                        'second_order_poly','third_order_poly','burkard','bioscience',
                                        'one_term_scaled_2d', 'one_term_standard_2d', 'two_term_standard_2d',
                                        'three_term_standard_2d', 'log_2d_b10','asymptotic_exponential'], return_name = False):
    rmse_list,mae_list,ypred_list = [],[],[]
    out_dict = {}
    fi = 1
    for f in function_list:
        try:
            rmseo,maeo,ypredo = test_fit(x,y,eval(f))
            rmse_list.append(rmseo)
            #mae_list.append(maeo)
            #ypred_list.append(ypredo)
            if return_name:
                out_dict[rmseo] = f
            else:
                out_dict[rmseo] = fi
        except:
            x = 0
        fi += 1

    try:

        min_rmse = min(rmse_list)

        to_return = out_dict[min_rmse]

        return to_return, min_rmse
    except:
        return 0,0


######################################################################################
##############################################################
#Reduces array to it divides without a remainder- for aggegating
def int_aggregate_dimensions(in_array,factor):
    factor = int(factor)
    s = in_array.shape
    while s[0]%factor != 0:
        in_array = in_array[:-1,:]
        s = in_array.shape
        print s
    while s[1]%factor != 0:
        in_array = in_array[:,:-1]
        s = in_array.shape
        print s
    return in_array
###############################################################
#Function to aggregate a numpy array by 2x
#Possible funs are: mean,min,max,std
#Adapted from: http://stackoverflow.com/questions/14916545/numpy-rebinning-a-2d-array
def aggregate_array(in_array, factor = 2, fun = 'mean'):
    s = in_array.shape

    factor = int(factor)
    in_array = int_aggregate_dimensions(in_array,factor)
    new_s = (s[0]/factor,factor,s[-1]/factor,factor)

    a_view = in_array.reshape(new_s)
    in_array = None

    exec('a_out = a_view.'+fun+'(axis = 3).'+fun+'(axis = 1)')

    return a_out

##############################################################
#Function to aggregate raster
def aggregate_raster(in_raster,out_raster, factor = 2, ignore_no_data = True):
    factor = int(factor)

    #Get info about raster
    ri = raster_info(in_raster)

    #Find the output resolution
    res = ri['res']
    out_res = float(res) *factor

    #Find no data
    no_data = ri['no_data']

    #Set up the transform
    t = ri['transform']
    out_transform = [t[0], out_res,t[2],t[3],t[4],-1*out_res]


    ti = None

    #Iterate through the bands
    for b in range(1,ri['bands']+1):

        #Read in raster of band n
        r = raster(in_raster,'',b)

        if no_data != None and ignore_no_data:
            print 'Masking no data'
            r = numpy.ma.masked_equal(r,no_data)

        print 'Aggregating band:', b

        #Aggregate the raster
        ot = aggregate_array(r,factor)
        r = None

        #Initialize the output raster if not already done
        if ti == None:
            width = ot.shape[1]
            height = ot.shape[0]
            ti = tiled_image(out_raster,'',width,height,ri['bands'],ri['dt'],out_transform,ri['projection'],'HFA',True,120000,True,out_no_data = ri['no_data'])

        #Add degraded raster to output
        ti.add_tile(ot,0,0, b)


        ot = None

    ti.rm()
    brick_info(out_raster,True)
##############################################################
########################################################################################
#Provides a quick mosaic method for on-the-fly tiled array writing to a larger raster
#Designed to avoid writing individual tiles, and then mosaicking them after all tiles are created
#The tiled_image object is really a gdal driver instance of the template image
#Individual sections of the driver can be written without bringing all tiles into memory at once
#Since a Numpy array is read in, all projection infomation must be provided within the template image
#The datatype (dt) can be overridden to a desired type regardless of the template's datatype
class tiled_image:
    def __init__(self, output, template_image = '', width = '', height = '', bands = '', dt = '', transform = '', projection = '', df = 'HFA', outline_tiles = False, size_limit_kb = 120000, make_output = True, ct = '', names = '', out_no_data = '',compression = False):
        df = format_dict[os.path.splitext(output)[1]]
        self.output = output
        if template_image != '':
            t_info = raster_info(template_image)
            self.projection, self.transform = t_info['projection'], t_info['transform']
        else:
            self.projection, self.transform = projection, transform

        if template_image != '':

            self.width, self.height = t_info['width'], t_info['height']
        else:
            self.width, self.height = width, height
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

        self.names = names
        self.ct = ct
        self.out_no_data = out_no_data
        if not make_output or os.path.exists(output):
            print 'Opening output in update mode'
            self.ds = gdal.Open(output, gdal.GA_Update)
        else:
            print 'Initializing output raster:', output
            driver = gdal.GetDriverByName(df)
            if compression:
                print 'Setting compression'
                self.ds = driver.Create(output, self.width, self.height, self.bands, eval(self.gdal_dt), ['COMPRESS=LZW'])
            else:
                self.ds = driver.Create(output, self.width, self.height, self.bands, eval(self.gdal_dt))
            try:
                self.ds.SetProjection(self.projection)
            except:
                print 'Cannot set the projection'
                print 'Likely because format is:', df
            try:
                self.ds.SetGeoTransform(self.transform)
            except:
                print 'Cannot set the transformation'
                print 'Likely because format is:', df

        if template_image != '' and outline_tiles == True:
            #Sets up the chunk size
            self.template_image = template_image
            self.size_limit_kb = size_limit_kb
            if os.path.exists(os.path.splitext(template_image)[0] + '.ige') == True:
                self.file_size =  os.path.getsize(os.path.splitext(template_image)[0] + '.ige')/1024.0
            else:
                self.file_size =  os.path.getsize(template_image)/1024.0
            self.pixel_count = self.height * self.width
            self.chunk_pointer_maker(size_limit_kb)
###########################################################################################
    #Function that sets up the chunk size based on the specified memory size allocation
    def chunk_pointer_maker(self, size_limit_kb = 100):
        #Calculates the size of the chunk by pixel count
        chunk_no = math.ceil(self.file_size/size_limit_kb)
        pixel_size = float(self.file_size)/ float(self.pixel_count)
        pixels_per_chunk = math.ceil(self.pixel_count/ chunk_no)
        pixels_per_chunk_band = math.ceil(pixels_per_chunk/ self.bands)
        chunk_no_x = math.ceil(math.sqrt(chunk_no))
        chunk_no_y = chunk_no_x
        chunk_size_x = math.ceil(self.width/ chunk_no_x)
        chunk_size_y = math.ceil(self.height/ chunk_no_y)
        self.chunk_size_x = chunk_size_x
        self.chunk_size_y = chunk_size_y
        #Sets the preliminary break points of the pixels
        break_points_x = range(0, int(self.width), int(chunk_size_x))
        break_points_y = range(0, int(self.height), int(chunk_size_y))

        #Sets up the final chunk_list
        #Chunk_list is a list of the chunks
        #Each chunk has the starting_x, starting_y, width_in_pixels, height_in_pixels
        #This is intended to feed into the brick function within the r_numpy_lib.py library
        self.chunk_list = []
        for bp_x in break_points_x:
            stx = bp_x
            spx = bp_x + chunk_size_x
            if spx > self.width:
                spx = self.width
            t_width = spx- stx
            for bp_y in break_points_y:
                sty = bp_y
                spy = bp_y + chunk_size_y
                if spy > self.height:
                    spy = self.height
                t_height = spy - sty
                self.chunk_list.append([stx, sty, int(t_width), int(t_height)])

        print 'There are', len(self.chunk_list),'chunks to process'

    def add_tile(self, in_array, x_offset, y_offset, specific_band = '', overlap_function = None):
        print type(in_array)
        if type(in_array) == list:
            in_array = numpy.array(in_array)

        dims = in_array.ndim
        if dims == 2:
            in_array = numpy.array([in_array])
        if len(in_array) > self.bands:
            band_range = self.bands
        else:
            band_range = len(in_array)
        print 'Writing pixel values for offsets:', x_offset, y_offset
        if specific_band == '':
            for band in range(band_range):
                band  += 1
                #try:
                if self.ct != '':
                    self.ds.GetRasterBand(band).SetRasterColorTable(self.ct)
                if self.names != '' and self.names != None:
                    print 'putting names', self.names
                    self.ds.GetRasterBand(band).SetRasterCategoryNames(self.names)
                if self.out_no_data != '' and self.out_no_data != None:
                    self.ds.GetRasterBand(band).SetNoDataValue(self.out_no_data)
                if overlap_function != None and overlap_function != '' and overlap_function != 'mask':
                    #at =
                    print 'Reading in overlap area'
                    try:
                        nat = numpy.array([self.ds.GetRasterBand(band).ReadAsArray(x_offset, y_offset, in_array.shape[2], in_array.shape[1]).astype(self.numpy_dt), in_array[band-1]])
                        #at = None
                        call = 'self.ds.GetRasterBand(band).WriteArray('+overlap_function+'(nat, axis = 0), x_offset, y_offset)'
                        print 'Applying', call
                        exec(call)
                    except:
                        print 'Could not read in overlap area'
                    nat = None
                elif overlap_function != None and overlap_function != '' and overlap_function == 'mask':

                    print 'Masking no data value:', self.out_no_data
                    #print numpy.max(in_array[band-1])
                    #print 'Numpy dt:', numpy_dt
                    from_array = self.ds.GetRasterBand(band).ReadAsArray(x_offset, y_offset, in_array.shape[2], in_array.shape[1]).astype(self.numpy_dt)
                    msk =  numpy.less_equal(in_array[band-1],self.out_no_data)
                    numpy.putmask(in_array[band-1],msk,from_array)
                    from_array = None
                    msk = None
                    self.ds.GetRasterBand(band).WriteArray(in_array[band-1],x_offset,y_offset)



                else:
                    self.ds.GetRasterBand(band).WriteArray(in_array[band-1], x_offset, y_offset)
                #except:
                #print 'Could not write', array[band-1]
        else:
            if self.ct != '':
                try:
                    self.ds.GetRasterBand(specific_band).SetRasterColorTable(self.ct)
                except:
                    print 'Could not set color table'
            if self.names != '':
                try:
                    self.ds.GetRasterBand(specific_band).SetRasterCategoryNames(self.names)
                except:
                    print 'Could not set names'
            if self.out_no_data != '':
                self.ds.GetRasterBand(specific_band).SetNoDataValue(self.out_no_data)
            self.ds.GetRasterBand(specific_band).WriteArray(in_array[0], x_offset, y_offset)
        in_array = None
    def rm(self):
        try:
            self.ds = None
        except:
            x = 'oops'


#######################################################################################
#Will write a numpy array to a raster
#Byte, UInt16, Int16, UInt32, Int32, Float32, Float6
def write_raster(numpy_array,output_name, template = '', df = 'HFA', dt = 'Int16', width = '', height = '', bands = 1, projection = '', transform = '', ct = '', names = '', out_no_data = '',assume_ct_names = True, compress = False):

    df = format_dict[os.path.splitext(output_name)[1]]
    if numpy_or_gdal(dt) == 'numpy':

        dt = dt_converter(dt)

    dt = 'gdal.GDT_' + dt
    if out_no_data == '' and template != '':
        if raster_info(template)['no_data'] != None:
            out_no_data = raster_info(template)['no_data']

    if template != '' and transform == '':
        rast = gdal.Open(template)
        width = rast.RasterXSize
        height = rast.RasterYSize
        #bands = rast.RasterCount
        projection = rast.GetProjection()
        rast = None
    if assume_ct_names and template != '' and (names == '' or names == None) and (ct == '' or ct == None) :
        ct, names, b111, rast111 = color_table_and_names(template, band = 1)
    if transform == '':
        rast = gdal.Open(template)
        transform = rast.GetGeoTransform()
    driver = gdal.GetDriverByName(df)
    if not compress:
        ds = driver.Create(output_name, width, height, bands, eval(dt))
    else:
        ds = driver.Create(output_name, width, height, bands, eval(dt),['COMPRESS=LZW'])
    ds.SetProjection(projection)
    ds.SetGeoTransform(transform)
    print 'Writing: ' + output_name.split('/')[-1]
    print 'Datatype of ' + output_name.split('/')[-1] + ' is: ' + dt
    if bands > 1:
        for band in range(1,bands + 1):


            ds.GetRasterBand(band).WriteArray(numpy_array[band-1])
            if ct != '' and ct != None:
                ds.GetRasterBand(band).SetRasterColorTable(ct)

            if names != '' and names != None:
                try:
                    ds.GetRasterBand(1).SetRasterCategoryNames(names)
                except:
                    print 'Could not write category names'
            if out_no_data != '':
                ds.GetRasterBand(band).SetNoDataValue(out_no_data)
    else:

        if ct != '' and ct != None:
            ds.GetRasterBand(1).SetRasterColorTable(ct)

        if names != '' and names != None:
            try:
                ds.GetRasterBand(1).SetRasterCategoryNames(names)
            except:
                print 'Could not write category names'
        if out_no_data != '':
            try:
                ds.GetRasterBand(1).SetNoDataValue(out_no_data)
            except:
                print 'Could not set no data value', out_no_data
        ds.GetRasterBand(1).WriteArray(numpy_array)
    return output_name
    ds = None
    numpy_array = None
    rast = None

##ti = 'W:/03_Data-Archive/02_Inputs/Landsat_Data/4126/Scenes/glovis/p041r026_distbYear_flt'
##to = 'W:/03_Data-Archive/02_Inputs/Landsat_Data/VCT_Outputs/Mosaicked_Outputs/distbYear_flt_first_distb_mosaic_near_w_color2.img'
##r = raster(ti)
###ct, nms, b, r1 = color_table_and_names(ti)
##ct = gdal.ColorTable()
###ct.SetColorEntry(0, (0, 0, 0, 255))
###ct.SetColorEntry(1, (0, 211, 0, 255))
###ct.SetColorEntry(2, (211, 0, 0, 255))
##ct.CreateColorRamp(1, (0, 211, 0, 255), 45, (211, 0, 0, 255))
###names = ['Unclassified','Nonforest', 'Forest']
##write_raster(r, to, ti, ct = ct)
##
##r = None
##del r
######################################################################################
def color_table_and_names(image, band = 1):
    rast = gdal.Open(image)
    b1 = rast.GetRasterBand(1)
    ct = b1.GetRasterColorTable()
    names = b1.GetRasterCategoryNames()
    return ct, names, b1, rast

color_dict = {'green' : (0, 200, 0, 255),
                  'red' : (200, 0, 0, 255),
                  'blue' : (0, 0, 200, 255),
                   'light_blue':(0, 102, 255,255),
                   'light_purple':(235, 153, 235),
                  'orange' : (255, 128, 0, 255),
                  'yellow' : (255, 255, 0, 255),
                  'gray' : (224, 224, 224, 255)
                  }
######################################################################################
#Function for creating a gdal color ramp
#Uses a numpy array to find the min and max and then creates a color table using those values
#The array must be positive

def min_max_color_ramp(array, cmin = 'red', cmax = 'green', gray_zero = True):

    print 'Creating min max color table'
    Min = int(numpy.amin(array))
    if Min <= 0:
        Min = 1
    Max = int(numpy.amax(array))
    ct = gdal.ColorTable()
    ct.CreateColorRamp(Min, color_dict[cmin], Max, color_dict[cmax])
    if gray_zero:
        ct.SetColorEntry(0, color_dict['gray'])
    return ct
##############################################################
######################################################################################
#Function for creating a gdal color ramp
#Uses a numpy array to find the min and max and then creates a color table using those values
#The array must be positive
def min_max_color_ramp2(Min,Max, cmin = 'red', cmax = 'green', gray_zero = True):

    print 'Creating min max color table'
##    Min = int(numpy.amin(array))
##    if Min <= 0:
##        Min = 1
##    Max = int(numpy.amax(array))
    ct = gdal.ColorTable()
    ct.CreateColorRamp(Min, color_dict[cmin], Max, color_dict[cmax])
    if gray_zero:
        ct.SetColorEntry(0, color_dict['gray'])
    return ct
##############################################################
def stack_report(image_list, output_name):
    report_name = os.path.splitext(output_name)[0] + '_report.txt'
    if os.path.exists(report_name) == False:
        report_lines = 'Stack report for: ' + output_name + '\n'
        report_lines += 'Created: ' + now()+ '\n\n'
        report_lines += 'Stacked images:\n'
        for image in image_list:
            report_lines += image + '\n'
        ro = open(report_name, 'w')
        ro.writelines(report_lines)
        ro.close()
##############################################################
#Stacks a list of rasters
#All rasters must be of the exact same extent
#Should use the
def stack(image_list = [], output_name = '', template = '', df = 'HFA', dt = '', width = '', height = '', projection = '', transform = '', array_list = False, color_table = '', category_names = '', out_no_data = '', report = True,guiable = True):
    if image_list == []:
        image_list = str(askopenfilenames(title = 'Select Rasters to stack',filetypes=[("IMAGINE","*.img"),("tif","*.tif")])).split(' ')
        print image_list
    if output_name == '':
        output_name = str(asksaveasfilename(title = 'Select output image name',initialdir = cwd,filetypes=[("IMAGINE","*.img"),("tif","*.tif")]))

    if array_list:
        image_list = numpy.array(image_list)
        if image_list.ndim == 2:
            image_list = numpy.array([image_list])

    if dt == '' and array_list == False:
        info = raster_info(image_list[0])
        dt = info['dt']
    elif dt == '' and array_list == True:
        info = raster_info(template)
        dt = info['dt']
    if out_no_data == '' and template != '':
        if raster_info(template)['no_data'] != None:
            out_no_data = raster_info(template)['no_data']
    if numpy_or_gdal(dt) == 'numpy':

        dt = dt_converter(dt)
    numpy_dt = dt_converter(dt)
    gdal_dt = 'gdal.GDT_' + dt
    print gdal_dt
    if template != '':
        rast = gdal.Open(template)
        width = rast.RasterXSize
        height = rast.RasterYSize
        if projection == '':
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
    if (category_names == '' or category_names == None) and (color_table == '' or color_table == None) and template != '':
        color_table, category_names, b111, rast111 = color_table_and_names(template, band = 1)
    df = format_dict[os.path.splitext(output_name)[1]]
    driver = gdal.GetDriverByName(df)
    print bands
    print 'df',df
    ds = driver.Create(output_name, width, height, bands, eval(gdal_dt))

    try:
        ds.SetProjection(projection)
        ds.SetGeoTransform(transform)
    except:
        print 'Could not set spatial info'
    if color_table != '' and color_table != None:
        try:
            ds.GetRasterBand(1).SetRasterColorTable(color_table)
        except:
            print 'Could not write color table'
    if category_names != '' and category_names != None:
        try:
            ds.GetRasterBand(1).SetRasterCategoryNames(category_names)
        except:
            print 'Could not write category names'
    print 'Writing: ' + output_name.split('/')[-1]
    print 'Datatype of ' + output_name.split('/')[-1] + ' is: ' + dt
    for band in range(bands):
        print 'Stacking band:', image_list[band]
        if array_list == False:
            array = raster(image_list[band], dt = numpy_dt)
        elif array_list == True:
            array = image_list[band]
        if out_no_data != '' and out_no_data != None:
            ds.GetRasterBand(band + 1).SetNoDataValue(out_no_data)
        ds.GetRasterBand(band + 1).WriteArray(array)
    if report and array_list == False:
        stack_report(image_list, output_name)
    return output_name
    ds = None
    array = None
    rast = None
##Dir = 'C:/Users/ihousman/Downloads/20e71921f819ee7ac81687c4c43ba3a8/'
##tifs = glob(Dir, '.tif')
##out = Dir + 'test_stack.img'
##stack(tifs,out,tifs[0])
##brick_info(out, True)
######################################################################################
#Restacks a specified list of bands from a stack into the specified order in the list
def restack(stack = '', output_name = '', template = '', band_list = [], df = 'HFA', dt = '', width = '', height = '', projection = '', transform = '', out_no_data = '',guiable = True):
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
        if out_no_data != '':
            ds.GetRasterBand(band + 1).SetNoDataValue(out_no_data)
        ds.GetRasterBand(band + 1).WriteArray(array)
        if template != '' and template != None:
            color_table, category_names, b1, rast = color_table_and_names(template, band = 1)
        else:
            color_table,category_names = None,None
        if color_table != '' and color_table != None:
            try:
                ds.GetRasterBand(1).SetRasterColorTable(color_table)
            except:
                print 'Could not write color table'
        if category_names != '' and category_names != None:
            try:
                ds.GetRasterBand(1).SetRasterCategoryNames(category_names)
            except:
                print 'Could not write category names'
    ds = None
    array = None
    rast = None
    return output_name
######################################################################################
def shift_raster(in_raster, shift_x, shift_y):
    rast = gdal.Open(in_raster, gdal.GA_Update)
    info = raster_info(in_raster)
    coords = info['coords']
    transform =  info['transform']
    transform = [transform[0] + shift_x, transform[1], transform[2], transform[3] + shift_y, transform[4], transform[5]]
    rast.SetGeoTransform(transform)
    rast = None
#image = 'A:/IansPlayground/vj_play/fid_49/zone40_Path29Row26_tcc_masked_RF_9030_CorrBias_TCC_Grouped_NoDups_surface_reflectance_albers_float_30m_shift_30.img'
#shift_raster(image,30,0)
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
        if os.path.splitext(pred)[1] == '.shp':
            coords = shape_info(pred)['coords']
        else:
            coords = raster_info(pred)['coords']
        extent_list.append(coords)

    extent_list = numpy.array(extent_list)

    mins = numpy.amin(extent_list, axis = 0)
    maxes = numpy.amax(extent_list, axis = 0)
    intersection = [maxes[0],maxes[1],mins[2],mins[3]]

    print 'The intersection coords of are', intersection
    return intersection
######################################################################################
def new_clip(image, output, clip_to_file, out_no_data = '', band_list = [], Buffer = 0, ct = '',names = '',dt = ''):
    if os.path.exists(output) == False:
        if type(clip_to_file) == list:
            try:
                clip_coords = intersection_coords(clip_to_file)
            except:
                clip_coords = clip_to_file
                print 'Already have the clip coords'
                print 'They are', clip_coords
        elif os.path.splitext(clip_to_file)[1] == '.shp':
            clip_info = shape_info(clip_to_file)
            clip_coords = clip_info['coords']


        else:
            clip_info = raster_info(clip_to_file)
            clip_coords = clip_info['coords']
        if Buffer != None and Buffer != '' and Buffer != 0:
            clip_coords = [clip_coords[0] - Buffer, clip_coords[1] -Buffer, clip_coords[2] + Buffer, clip_coords[3] + Buffer]
        if type(image) == list:
            r_info = raster_info(image[0])
            ctt, namest, b1, rast = color_table_and_names(image[0], band = 1)
        else:
            r_info = raster_info(image)
            ctt, namest, b1, rast = color_table_and_names(image, band = 1)
        orig_coords = r_info['coords']
        res = r_info['res']
        orig_width = r_info['width']
        orig_height = r_info['height']

        xo = int(math.floor((clip_coords[0] - orig_coords[0])/res))
        yo = int(math.floor((orig_coords[-1] - clip_coords[-1])/res))
        if xo < 0:
            xo = 0
        if yo < 0:
            yo = 0
        if xo == 0:
            w = int(math.floor((clip_coords[2] - clip_coords[0])/res))
        else:
            w = int(math.floor((clip_coords[2] - clip_coords[0])/res))
        if yo == 0:
            h = int(math.floor((orig_coords[-1] - clip_coords[1])/res))
        else:
            h = int(math.floor((clip_coords[-1] - clip_coords[1])/res))

        if h + yo > orig_height:
            h = orig_height-yo
        if w + xo > orig_width:
            w = orig_width - xo

        if out_no_data == '':
            out_no_data = r_info['no_data']
        print 'clip to coords', clip_coords
        print 'Out no data value:', out_no_data
        print 'Res:', res
        print 'xo,yo,w,h:',xo,yo,w,h
        print 'Orig width and height:',orig_width, orig_height
        print 'Output name:', output
        out_transform = [orig_coords[0] + (xo * res), r_info['res'], 0.0, orig_coords[-1] - (yo * res), 0.0, -1 * r_info['res']]

        if ct == '' or ct == None:
            ct = ctt
            print 'The color table is', ct
        if dt == '' or dt == None:
            dt = r_info['dt']
        if names == '' or names == None:
            names = namest
        print 'The datatype is', dt
        if band_list == []:
                band_list = range(1,r_info['bands'] + 1)
        ti = tiled_image(output,  bands = len(band_list),dt =dt, width = w, height = h, projection = r_info['projection'], transform = out_transform, out_no_data = out_no_data,ct = ct, names = names)
        if type(image) == list:
            #b = brick(image,dt,xo,yo,w,h,image_list = True )
            for img in image:
                r = raster(img,dt,b,xo,yo,w,h)
                ti.add_tile(r,0,0,b)
                r = None
        else:

            for b in band_list:
                r = raster(image,dt,b,xo,yo,w,h)
                ti.add_tile(r,0,0,b)
                r = None
            #b = brick(image, dt, xo,yo, w, h, band_list = band_list)
        ti.rm()
        #stack(b, output,  dt =dt, width = w, height = h, projection = r_info['projection'], transform = out_transform, array_list = True, color_table = ct, category_names = names, out_no_data = out_no_data)
        #b = None
##    else:
##        print 'Output:', output, 'already exists'
##in_raster = '//166.2.126.38/Working/RTFD_TDD/MZ_13_fix_mask/mz13_fix_t.tif'
##clip_extent ='//166.2.126.38/Working/RTFD_TDD/TDD_Processing/2014/121/linear_fit_outputs_121_post_processing/2014_121_8_14_tdd_persistence_3class.img'
##
##out_raster = '//166.2.126.38/Working/RTFD_TDD/MZ_13_fix_mask/mz13_fix_t_clip.tif'
##out_raster_recode = '//166.2.126.38/Working/RTFD_TDD/MZ_13_fix_mask/mz13_fix_t_clip_recode.tif'
##r = raster(out_raster)
##r[r == 255] = 254
##r[r == 0] = 255
##r[r == 1]  = 0
##
##write_raster(r,out_raster_recode,out_raster, dt = 'Byte')
##r = None
##new_clip(in_raster,out_raster,clip_extent)
######################################################################################
def batch_new_clip(images, out_dir, study_area= '',out_extension = '_clip.img', no_data = '',band_list = [],dt = ''):
    #if study_area == '' or study_area == None:
        #study_area = images
    if study_area == '' or study_area == None:
        study_area = intersection_coords(images)
    #print 'Study area:', study_area
    out_list = []
    for image in images:
        if os.path.splitext(image)[1] != '.shp':
            out_image = out_dir + base(image) + out_extension
            out_list.append(out_image)
            if os.path.exists(out_image) == False:
                print 'Clipping', base(image)

                new_clip(image,out_image,study_area, no_data, band_list = band_list)
                print 'Computing stats for', out_image
                #brick_info(out_image, True)
    return out_list
######################################################################################
def clip_set_proj(in_image, out_image, wkt,clip_no = 50, out_no_data = 255):
    if os.path.exists(out_image) == False:
        try:
            od = os.path.dirname(out_image)
            check_dir(od)
            rit = raster_info(in_image)
            width,height =  rit['width'], rit['height']
            oh= height - clip_no

            b = brick(in_image, '', 0,0, width, oh)
            #ct, names, b1, rast = color_table_and_names(pi)
            stack(b, out_image,  dt = rit['dt'], width = width, height =oh, projection = wkt, transform = rit['transform'], array_list = True,out_no_data = out_no_data)#, color_table = ct)
        except:
            print 'Could not clip and set projection for', in_image
        b = None
    else:
        print out_image, 'already exists'
    return out_image
######################################################################################
#Will clip an image to the common extent of a list of images
#Can return an array of zeros of the common extent and/or can clip a single or multi-band image
#Returns a 3-d array.  If a single band raster is provided, the array is returned as the first within a list with length = 1
def clip(image = '', output_name = '', clip_extent_image_list = [], array_only = False, zeros_only = False, dt = '', out_no_data = '',guiable = True):
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

    if type(clip_extent_image_list) == list:
        coords = intersection_coords(clip_extent_image_list)
    elif os.path.splitext(clip_extent_image_list)[1] == '.shp':
        s_info = shape_info(clip_extent_image_list)
        coords = s_info['coords']
        print coords
    else:
        r_info = raster_info(clip_extent_image_list)
        coords = r_info['coords']
    rast = gdal.Open(image)
    transform = rast.GetGeoTransform()

    projection = rast.GetProjection()
    res_orig = transform[1]
    resolution = res_orig

    ct, names, b1t, rastt = color_table_and_names(image, band = 1)
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
##    xo =row_offset
##    yo = column_offset
##    w = out_ncolumn
##    h = out_nrow
##    print xo,yo,w,h
##    array_list = brick(image, dt, xo,yo,w,h)

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
        stack(array_list, output_name = output_name, width = int(out_ncolumn), height = int(out_nrow), projection = projection, transform = out_transform,dt = dt, array_list = True, color_table = ct, category_names = names, out_no_data = out_no_data)
        raster_info(output_name, get_stats = True)
##        #write_raster(array, output_name ,dt = dt,width = int(out_ncolumn), height = int(out_nrow), projection = projection, transform = out_transform)
##    else:
##        print 'Array_only is True'
##        print 'Returned array with following dims:', numpy.shape(array)
    rast = None
    array = None
    return array_list

    array_list = None
######################################################################################
#Clips and snaps a list of rasters to the common extent of the rasters in the list
#All rasters must be the sampe projection and spatial resolution
#Rasters can be of different band numbers
def clip_list(input_list = [], output_suffix = '_clip.img', output_dir = '',dt = '', overwrite = True, guiable = True, out_no_data = ''):
    if input_list == []:
        input_list = str(askopenfilenames(title = 'Select images to clip to common extent',filetypes=[("IMAGINE","*.img"),("tif","*.tif")])).split(' ')


    out_list = []

    for Input in input_list:
        success = True
        if output_dir != '':
            output = output_dir + base(Input) + output_suffix
        else:
            output = os.path.splitext(Input)[0] + output_suffix
        if os.path.exists(output) == False or overwrite == True:
            try:
                clip(Input, output, input_list, array_only = False, dt = dt, out_no_data = out_no_data)


            except:
                print 'Could not clip', Input
                success = False
        if success:
            out_list.append(output)

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

    in_rast = None
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
def find_count(in_string, what_to_find):
    fc = 0
    for i in range(len(in_string)):
        if in_string.find(what_to_find,i) ==i:
            fc += 1
    return fc
def smart_sort(in_list, year_list = range(1980, 2030), year_query = 'base(il).find(str(year))'):
    out_list = []
    out_year_list = []
    t_lists = []
    duplicate_list = []
    year_in_all = []
    year_not_in_all_images = []
    year_in_all_images = []
    out_years = []
    big_list = []
    for year in year_list:
        c = 0
        y = str(year)
        tl=[year]
        for il in in_list:
            bil = base(il)
            #print year, bil
            if bil.find(y) > -1:
                tl.append(il)
                c += 1
        big_list.append(tl)

    for bl in big_list:
        if len(bl)  > 1:
            out_years.append(bl[0])
        if len(bl) == 2:
            out_list.append(bl[1])
        elif len(bl) > 2:
            for image in bl[1:]:
                if find_count(base(image), str(bl[0])) > 1:
                    out_list.append(image)
    return out_list, out_years
def simple_smart_sort(in_list, year_list = range(1980, 2030), year_query = 'base(il).find(str(year))'):
    yo = []
    io = []
    for year in year_list:
        for il in in_list:
            exec('f = ' + year_query)
            if f > -1:
                yo.append(int(year))
                io.append(il)
    return io,yo
##############################################################################################
#Code source: http://gis.stackexchange.com/questions/77993/issue-trying-to-create-zonal-statistics-using-gdal-and-python
def zonal_stats(feat, input_zone_polygon, input_value_raster, statistic = 'numpy.mean',band = 1, no_data_value = ''):
    if no_data_value == '':
        ri = raster_info(input_value_raster)
        no_data_value = ri['no_data']

    # Open data
    raster = gdal.Open(input_value_raster)
    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()

    # Get raster georeference info
    transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    # Get extent of feat
    geom = feat.GetGeometryRef()
    if (geom.GetGeometryName() == 'MULTIPOLYGON'):
        count = 0
        pointsX = []; pointsY = []
        for polygon in geom:
            geomInner = geom.GetGeometryRef(count)
            ring = geomInner.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            for p in range(numpoints):
                    lon, lat, z = ring.GetPoint(p)
                    pointsX.append(lon)
                    pointsY.append(lat)
            count += 1
    elif (geom.GetGeometryName() == 'POLYGON'):
        ring = geom.GetGeometryRef(0)
        numpoints = ring.GetPointCount()
        pointsX = []; pointsY = []
        for p in range(numpoints):
                lon, lat, z = ring.GetPoint(p)
                pointsX.append(lon)
                pointsY.append(lat)

    else:
        sys.exit()

    xmin = min(pointsX)
    xmax = max(pointsX)
    ymin = min(pointsY)
    ymax = max(pointsY)

    # Specify offset and rows and columns to read
    xoff = int(round((float(xmin) - float(xOrigin))/float(pixelWidth)))
    yoff = int(round((float(ymax) - float(yOrigin))/float(pixelHeight)))
    xcount = int((xmax - xmin)/pixelWidth)+1
    ycount = int((ymax - ymin)/pixelWidth)+1
##    xmin = array_coord_list[0]
##    ymax = array_coord_list[-1]
##    offsetx = int(round((float(proj_coords[0]) - float(xmin))/float(res)))
##    offsety = int(round((float(ymax) - float(proj_coords[1]))/ float(res)))
##    return [offsetx, offsety]

    # Create memory target raster
    target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
        xmin, pixelWidth, 0,
        ymax, 0, pixelHeight,
    ))

    # Create for target raster the same projection as for the value raster
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjectionRef())
    target_ds.SetProjection(raster_srs.ExportToWkt())

    # Rasterize zone polygon to raster
    gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])

    # Read raster as arrays
    banddataraster = raster.GetRasterBand(band)
    dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float).flatten()

    bandmask = target_ds.GetRasterBand(1)
    datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float).flatten()

    # Mask zone of raster
    zoneraster = dataraster[datamask != False]
    #zoneraster = numpy.ma.masked_array(dataraster,  numpy.logical_not(datamask))
##    if no_data_value != '' and no_data_value != None:
##        zoneraster = zoneraster[zoneraster != no_data_value]

    # Calculate statistics of zonal raster
    exec('x = ' +statistic +'(zoneraster)')
    #print zoneraster,len(zoneraster),x
    return x

def mode(in_array):
    if type(in_array) == list:
        in_array = numpy.array(in_array)

    m = numpy.argmax(numpy.bincount(in_array.astype('u2').flatten()))
    #return m
##    print in_array
##    print m
    return m

def diff_from_first(in_array, axis = 0):
    out = numpy.empty_like(in_array)[:-1]
    print len(out)

    i = 0
    for l in in_array[1:]:

        out[i] =l- in_array[0]
        i += 1
    in_array = None
    del in_array
    return out
def running_sum(in_array, axis = 0):
    out = numpy.empty_like(in_array)[:-1]
    print len(out)
    out[0] = in_array[0] + in_array[1]
    i = 1
    for l in in_array[2:]:

        out[i] =l+out[i-1]
        i += 1
    in_array = None
    del in_array
    return out

##image = 'R:/NAFD/Landtrendr/tSAT/tSTAT/Test_Data/Michigan_Forest_Z_Clip.tif'
###r = brick(image)
##r = numpy.arange(100).reshape((4,5,5))
##print r
##o = diff_from_first(r)
##o = running_sum(r)
##print o
##
##r = None
##i = range(99)
##i.append(60)
##x = numpy.array(i).reshape((2,50))
##x = numpy.ma.masked_inside(x,50,70)
###print x
##print numpy.ma.MaskedArray.nonzero(x)
###print numpy.ma.getdata(x)
##print mode(x)

def loop_zonal_stats(input_zone_polygon, input_value_raster, statistic = 'numpy.mean',band = 2, no_data_value = ''):
    if no_data_value == '':
        ri = raster_info(input_value_raster)
        no_data_value = ri['no_data']
    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()
    featList = range(lyr.GetFeatureCount())
    #statDict = {}
    statDict = []
    for FID in featList:
        print 'Computing ', statistic, 'for FID:',FID, no_data_value
        feat = lyr.GetFeature(FID)
        meanValue = zonal_stats(feat, input_zone_polygon, input_value_raster, statistic = statistic,band = band, no_data_value = no_data_value)
        #statDict[FID] = meanValue
        statDict.append(meanValue)
    return statDict

def zonal_stat(input_zone_polygon, input_value_raster, FID = 0, statistic = 'numpy.mean',band_list  = 'All', no_data_value = ''):
    if band_list.lower() == 'all':
        ii = raster_info(input_value_raster)
        band_list = range(1,ii['bands']+1)
    if no_data_value == '':
        ri = raster_info(input_value_raster)
        no_data_value = ri['no_data']
    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()
    featList = range(lyr.GetFeatureCount())
    feat = lyr.GetFeature(FID)
    statDict = {}

    out_list = []
    for band in band_list:
        meanValue = zonal_stats(feat, input_zone_polygon, input_value_raster, statistic = statistic,band = band, no_data_value = no_data_value)
        out_list.append(meanValue)
    return out_list

### Raster dataset
##raster_dir = 'R:/NAFD/Landtrendr/timesync2/test_data/images/'
### Vector dataset(zones)
##input_zone_polygon = 'R:/NAFD/Landtrendr/timesync2/test_data/sample/test_poly_sample.shp'
##ivrs = glob(raster_dir, '.img')
##for ivr in ivrs:
##    print zonal_stat(input_zone_polygon, ivr,0)
###########################################################################
#Taken from: http://www.xxki.com/tutorial/pukiwiki.php?cmd=read&page=Python%2FGDAL%20and%20OGR
def buffer_polygon(infile,outfile,buffdist):
    try:
        ds_in=ogr.Open( infile )
        lyr_in=ds_in.GetLayer( 0 )
        drv=ds_in.GetDriver()
        if os.path.exists( outfile ):
            drv.DeleteDataSource(outfile)
        ds_out = drv.CreateDataSource( outfile )

        layer = ds_out.CreateLayer( lyr_in.GetLayerDefn().GetName(), \
            lyr_in.GetSpatialRef(), ogr.wkbPolygon)
        n_fields = lyr_in.GetLayerDefn().GetFieldCount()
        for i in xrange ( lyr_in.GetLayerDefn().GetFieldCount() ):
            field_in = lyr_in.GetLayerDefn().GetFieldDefn( i )
            fielddef = ogr.FieldDefn( field_in.GetName(), field_in.GetType() )
            layer.CreateField ( fielddef )

        featuredefn = layer.GetLayerDefn()

        for feat in lyr_in:
            geom = feat.GetGeometryRef()
            #feature = ogr.Feature(featuredefn)
            #pdb.set_trace()
            feature = feat.Clone()
            feature.SetGeometry(geom.Buffer(float(buffdist)))
            #for in in xrange ( n_fields ):
                #feature.SetField (
            layer.CreateFeature(feature)
            del geom
        ds_out.Destroy()
    except:
        return False
    return True


###########################################################################
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

#Combines masks and assigns a unique index number to the mask pixels
def combine_masks(images, output, no_data = 0):
    dt = raster_info(images[0])['dt']
    base = empty_raster(images[0], dt = dt)
    i = 1
    for image in images:
        rast = raster(image, dt = dt)
        base[rast != no_data] = i
        i += 1
    write_raster(base, output, images[0], dt = dt)
    base = None
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
def mask(image = '', mask = '', output = '', dt = '', mask_no = 1, overwrite = True, guiable = True, mask_method = 'mult'):
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
            if mask_method == 'add':
                array = array * mask
                array = array + mask
            else:
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
def stack_clip(input_list = [], output_dir = '', output_suffix = '_intersection.img', dt = '', lt_no = 1, overwrite = True, out_no_data = '',guiable = True):
    if input_list == []:
        input_list = str(askopenfilenames(title = 'Select images to find common data extent\nMust be the same extent\nUse Clip_list to ensure the images are the same extent',filetypes=[("IMAGINE","*.img"),("tif","*.tif")])).split(' ')
    if output_dir == '':
        output_dir = str(askdirectory(initialdir = cwd, title = 'Please select an output directory')) + '/'



    if out_no_data == '':
        reassign_value = 0
    else:
        reassign_value = out_no_data
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

                array[base == 0] = reassign_value
                array_list.append(array)
                array = None
            #print input_list[0]
            print 'output',type(output)
            info = raster_info(Input)
            print info['height'], info['transform']

            stack(array_list, output_name = output,height = info['height'],width = info['width'], projection = info['projection'], transform = info['transform'], dt = info['dt'], out_no_data = out_no_data, array_list = True)
            raster_info(output, get_stats = True)
            array_list = None
            #write_raster(array, output, input_list[1], dt = dt)
            print
            print
        intersection_list.append(output)
    return intersection_list
    base = None
    array = None
##images = ['X:/Landsat/169069/tStat/169069_ndvi_stack_1990_2009_stats.linregress_slope.img', 'X:/Landsat/169068/tStat/169068_ndvi_stack_1990_2010_stats.linregress_slope.img']
##out_dir = 'X:/Regression_Calibration/'
##clips = clip_list(images, output_dir = out_dir, out_no_data = -9999, overwrite = False)
##
##stack_clip(clips, out_dir, dt = 'Int16',lt_no = -9998, out_no_data = -9999)
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
def unstack(stack = '', out_dir = '',dt = '', layers = 'All', overwrite = False, guiable = True,out_name = ''):
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
        if out_name == '' or out_name == None:

            if out_dir == '':
                out_name = os.path.splitext(stack)[0] + '_' + str(i) + '.img'
            else:
                out_name = out_dir + os.path.basename(os.path.splitext(stack)[0]) + '_' + str(i) + '.img'
        if os.path.exists(out_name) == False or overwrite == True:
            array = raster(stack, band_no = i, dt = dt)

            write_raster(array, out_name, stack, dt = dt, bands = 1)
            raster_info(out_name,1,True)
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

#Converts the format of a raster using the gdal_translate.exe
#Use 'HFA' for .img
def convert(Input = '', Output = '', Format = 'GTiff', gdal_dir = program_files_dir + '/FWTools2.4.7/bin/', dt = '', guiable = True):
    accepted_dts = ['Byte', 'Int16', 'UInt16', 'UInt32', 'Int32', 'Float32', 'Float64', 'CInt16', 'CInt32', 'CFloat32', 'CFloat64']
    Format = format_dict[os.path.splitext(Output)[1]]
    if Input == '':
        Input = str(askopenfilename(title = 'Select image to convert',filetypes=[("IMAGINE","*.img"),("tif","*.tif"),("ENVI","*.hdr")]))
        Output = str(asksaveasfilename(title = 'Select output image name with format extension',initialdir = cwd,filetypes=[("IMAGINE","*.img"),("tif","*.tif"),("ENVI","*.hdr")]))

        extension = os.path.splitext(Output)[1]
        Format = format_dict[extension]

        if os.path.splitext(Input)[1] == '.hdr':
            Input = os.path.splitext(Input)[0]
        if os.path.splitext(Output)[1] == '.hdr':
            Output = os.path.splitext(Output)[0]

    if dt != '' and dt in accepted_dts:
        dt = ' -ot ' + dt
    elif dt != '' and dt not in accepted_dts:
        dt = ''
        print 'Datatype:', dt, 'not accepted'
        print 'Must be', accepted_dts
    else:
        dt = ''
    gdal_call = gdal_dir + 'gdal_translate -of ' + Format + dt + ' ' + Input + ' ' + Output
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
    #images = images.reverse()
    for image in images:
        if convert_from_extension == '.hdr':
            image = os.path.splitext(image)[0]
        output = out_folder + os.path.basename(os.path.splitext(image)[0]) + extension_dict[out_format]
        if (os.path.exists(output) == False or overwrite == True) and output.find('toaBr') == -1:
            print image
            #raw_input()
            try:
                convert(image, output, Format = out_format)
            except:
                print 'Could not convert', image
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
        crs = '"+proj=' + proj + ' +zone=' + str(zone) + ' +datum=' + datum + '"'

    elif crs != '':
        crs = '"' + crs + '"'
    statement = gdal_dir + 'ogr2ogr -f "ESRI Shapefile" -t_srs ' + crs + ' "' + output + '" "' + shapefile + '"'
    print statement
    call = subprocess.Popen(statement)
    call.wait()
#####################################################################################################
def select_by_location(shp_to_clip, output, clip_extent, gdal_dir = gdal_dir, overwrite = True):
    if overwrite or os.path.exists(output) == False:
        if os.path.exists(output):
            try:
                delete_shapefile(output)
            except:
                print 'Could not delete', output

        statement = gdal_dir + 'ogr2ogr -f "ESRI Shapefile" ' + output + ' ' + shp_to_clip
        if type(clip_extent) == list:
            statement += ' -clipsrc ' + coords_to_gdal(clip_extent)
        elif os.path.splitext(clip_extent)[1] == '.shp':
            statement += ' -clipsrc "' + clip_extent + '"'
        elif os.path.splitext(clip_extent)[1] in format_dict.keys():
            print 'Extracting clip coords from raster'
            cs =raster_info(clip_extent)['gdal_coords']
            print cs
            statement += ' -clipsrc ' + cs
        print statement
        call = subprocess.Popen(statement)
        call.wait()
    else:
        print 'Output already exists'
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
def reproject(Input, output, crs = '', proj = 'utm', zone = '', datum = 'nad83' , res = '',resampling_method = 'cubic', clip_extent = '', no_data = 'NODATA', src_no_data = '', dst_no_data = '', cutline = '',Format = 'HFA', source_crs = '',dt = '', wm = 40, gdal_dir = gdal_dir):
    Format = format_dict[os.path.splitext(output)[1]]
    if type(clip_extent) == list:
        clip_extent = coords_to_gdal(clip_extent)
    if type(Input) == list:
        temp = Input
        Input = '"'
        for t in temp:
            Input += t + '" "'
        Input = Input[:-2]
    if source_crs != '' and source_crs != None:
        s_crs = ' -s_srs "' + source_crs + '" '
    else:
        s_crs = ''
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
    if cutline != '':
        cutline = ' -cutline ' + cutline
    if src_no_data != '' and dst_no_data != '':
        no_data = ' -srcnodata ' + str(src_no_data) + ' -dstnodata '+ str(dst_no_data)
    elif src_no_data != '':
        no_data = ' -srcnodata ' + str(src_no_data)
    elif dst_no_data != '':
        no_data = ' -dstnodata ' + str(dst_no_data)
    elif no_data != '':
        no_data = ' -srcnodata ' + str(no_data) + ' -dstnodata '+ str(no_data)
    if clip_extent != '':
        clip_extent = ' -te ' + clip_extent
    if dt != '':
        dt = ' -ot ' + str(dt) + ' '
    print 'Reprojecting:' ,Input.split('/')[-1]
    print
    if Format != '':
        ot = ' -of ' + Format
    gdal_call = gdal_dir + 'gdalwarp -wm '+str(wm)+' -multi' + ot +s_crs + dt+ no_data +cutline + crs + res + clip_extent +' -r ' + resampling_method + ' "' + Input + '" "' + output + '"'
    print gdal_call
    print
    call = subprocess.Popen(gdal_call)
    call.wait()

def gdal_clip(Input, output,clip_file, gdal_dir = gdal_dir):
    bounds = shape_info(clip_file)['coords']
    print bounds
    clip_extent = coords_to_gdal(bounds)
    print clip_extent
    Format = format_dict[os.path.splitext(output)[1]]
##    gdal_call = gdal_dir + 'gdal_translate -projwin ' + str(bounds[0]) + ' ' + str(bounds[1]) + ' ' + str(bounds[2]) + ' ' + str(bounds[3])  + ' -of ' + Format + ' "' +Input + '" "' + output + '"'
    gdal_call = gdal_dir + 'gdalwarp -cutline ' + clip_file + ' -of ' + Format + ' "' +Input + '" "' + output + '"'
    print gdal_call
    print
    call = subprocess.Popen(gdal_call)
    call.wait()
########################################################################################################################
def batch_reproject(image_list, out_folder, suffix = '_proj.img', clip_extent = '', res = '', crs = '', datum = '', zone = '', resampling_method = 'cubic',source_crs = ''):
    out_list = []
    for image in image_list:
        output = out_folder + os.path.basename(os.path.splitext(image)[0])+ suffix
        if os.path.exists(output) == False:
            reproject(image, output, zone = zone, datum = datum, crs = crs, res = res, resampling_method = resampling_method, clip_extent = clip_extent, source_crs = source_crs)
        out_list.append(output)
    return out_list
############################################################################
#Adapted from FW Tools in order to read and write color tables and class names if available
def gdal_sieve(Input, Output = None, threshold = 8, connectedness = 8,out_no_data = ''):
    ri = raster_info(Input)
    prog_func = gdal.TermProgress
    Format = format_dict[os.path.splitext(Output)[1]]
    ct, names, b1, rast = color_table_and_names(Input, band = 1)

    # =============================================================================
    # 	Verify we have next gen bindings with the sievefilter method.
    # =============================================================================
    try:
        gdal.SieveFilter
    except:
        print('')
        print('gdal.SieveFilter() not available.  You are likely using "old gen"')
        print('bindings or an older version of the next gen bindings.')
        print('')
        sys.exit(1)

    # =============================================================================
    #	Open source file
    # =============================================================================

    if Output is None:
        src_ds = gdal.Open( Input, gdal.GA_Update )
    else:
        src_ds = gdal.Open( Input, gdal.GA_ReadOnly )

    if src_ds is None:
        print('Unable to open ', Input)
        sys.exit(1)

    srcband = src_ds.GetRasterBand(1)



    # =============================================================================
    #       Create output file if one is specified.
    # =============================================================================

    if Output is not None:

        drv = gdal.GetDriverByName(Format)
        dst_ds = drv.Create( Output,src_ds.RasterXSize, src_ds.RasterYSize,1,
                             srcband.DataType,['COMPRESS=LZW'] )
        wkt = src_ds.GetProjection()
        if wkt != '':
            dst_ds.SetProjection( wkt )
        dst_ds.SetGeoTransform( src_ds.GetGeoTransform() )



        dstband = dst_ds.GetRasterBand(1)
    else:
        dstband = srcband
    if ct is not None:
        try:
            dstband.SetRasterColorTable(ct)
        except:
            print 'Could not write color table'
    if names is not None:
        try:
            dstband.SetRasterCategoryNames(names)
        except:
            print 'Could not write category names'
    if out_no_data == '' or out_no_data == None:
        out_no_data = ri['no_data']

    if out_no_data != '' and out_no_data != None:
        print 'Setting out no data to:', out_no_data
        dstband.SetNoDataValue(int(out_no_data))
    # =============================================================================
    #	Invoke algorithm.
    # =============================================================================
    result = gdal.SieveFilter(srcband, None, dstband, threshold, connectedness, callback = prog_func)

    ct = None
    names = None
    b1 = None
    rast = None


########################################################################################################################
#Function to convert a specified column from a specified dbf file into a list
#e.g. dbf_to_list(some_dbf_file, integer_column_number)
##def dbf_to_list(dbf_file, field_name):
##    if os.path.splitext(dbf_file)[1] == '.shp':
##        dbf_file = os.path.splitext(dbf_file)[0] + '.dbf'
##    #The next exception that is handled is handled within an if loop
##    #This exception would occur if a non .dbf file was entered
##    #First it finds wither the extension is not a .dbf by splitting the extension out
##    if os.path.splitext(dbf_file)[1] != '.dbf':
##        #Then the user is prompted with what occured and prompted to exit as above
##        print 'Must input a .dbf file'
##        print 'Cannot compile ' + dbf_file
##        raw_input('Press enter to continue')
##        sys.exit()
##
##    #Finally- the actual function code body
##    #First the dbf file is read in using the dbfpy Dbf function
##    db = dbf.Dbf(dbf_file)
##    #Db is now a dbf object within the dbfpy class
##
##    #Next find out how long the dbf is
##    rows = len(db)
##
##    #Set up a list variable to write the column numbers to
##    out_list = []
##
##    #Iterate through each row within the dbf
##    for row in range(rows):
##        #Add each number in the specified column number to the list
##        out_list.append(db[row][field_name])
##    db.close()
##    #Return the list
##    #This makes the entire function equal to the out_list
##    return out_list
################################################################
#Removes every instance of a piece of a string from a
def remove_all(in_string, remove_piece):
    while in_string.find(remove_piece) > -1:
        where = in_string.find(remove_piece)
        in_string = in_string[0:where] + in_string[where + len(remove_piece): len(in_string)]
    return in_string
#Rotates a 2-d array 90 degrees
def transpose(in_array):
    tab = in_array
    out_tab = []
    for row in range(len(tab[0])):
        temp = []
        for column in range(len(tab)):
            temp.append(tab[column][row])
        out_tab.append(temp)
    return out_tab
def reverse(inList):
    out = []
    for i in range(1,len(inList)+1):
        out.append(inList[-1*i])
    return out
def flatten_2d(in_list):
    out_list = []
    for i1 in range(len(in_list)):
        tl= in_list[i1]
        if type(tl) != list:
            tl = [tl]
        for i2 in tl:
            out_list.append(i2)
    return out_list
#Extracts a list of fields from a dbf or shp to a 2-d array and returns the array
def multiple_field_extraction(dbf, field_list, Transpose = True):
    tab = []
    if os.path.splitext(dbf)[1] == '.shp':
        dbf = os.path.splitext(dbf)[0] + '.dbf'
    for field in field_list:
        print 'Extracting field:', field
        temp = dbf_to_list(dbf, field)
        tab.append(temp)

    if Transpose == True:
        return transpose(tab)
    else:
        return tab
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
    if os.path.exists(output) == False:
        call = subprocess.Popen(statement)
        call.wait()
    else:
        print 'Already created', output
def explode_shapefile(shapefile, out_dir, field):
    check_dir(out_dir)
    field_list = dbf_to_list(shapefile, field)
    for entry in field_list:

        out = out_dir + base(shapefile) + '_' + str(entry) + '.shp'
        if os.path.exists(out) == False:
            print 'Extracting', os.path.basename(out)
            query = field + ' = ' + str(entry)
            print query
            select_by_attribute(shapefile, out, query)
##in_shp = 'X:/SA/Eastern_Province_Districts.shp'
##out_folder = 'X:/Summary_Zones/districts/'
##field = 'NAME_2'
##check_dir(out_folder)
##explode_shapefile(in_shp, out_folder, field)
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
def clip_shapefile(shapefile, extent_raster = '', extent_coords = '', output = '',gdal_dir = gdal_dir):
    if extent_raster != '':
        if os.path.splitext(extent_raster)[1] == '.shp':
            i = shape_info(extent_raster)
        else:
            i = raster_info(extent_raster)
        coords = i['gdal_coords']
    else:
        coords = extent_coords
    print coords
    statement = gdal_dir + 'ogr2ogr -f "ESRI Shapefile" '
    #if reproject and i != None:
        #statement += '-t_srs "' + i['proj4'] + '" '
    statement +=  '-clipsrc ' + coords + ' ' + output + ' ' + shapefile
    print statement
    call = subprocess.Popen(statement)
    call.wait()
##sa_shp = 'W:/03_Data-Archive/03_Process/Tech_Transfer/1Study_Area/now_now/AdminBndry_buff1km_Albers.shp'
##from_shp = 'C:/Road_Sheds/USA_roads.shp'
##si = shape_info(sa_shp)
##to_shp1 =os.path.splitext(from_shp)[0]+ '_albers.shp'
##to_shp2 =os.path.splitext(from_shp)[0]+ '_albers_clip.shp'
###reproject_shapefile(from_shp,to_shp1,si['proj4'])
##clip_shapefile(to_shp1, sa_shp,'',to_shp2)
########################################################################################################################
def landtrendr_coord_file_maker(input_coords, output_csv):
    out_list = 'integer,float,float\nplotid,X,Y\n'
    pid = 1
    for coord_set in input_coords:
        out_list += str(pid) + ',' + str(coord_set[0]) + ',' + str(coord_set[1]) + '\n'
        pid += 1
    out_list = out_list[:-1]
    print 'Writing', output_csv
    ocsvo = open(output_csv, 'w')
    ocsvo.writelines(out_list)
    ocsvo.close()
def write_xy_csv(xy_coords, csv_name):
    print xy_coords
    if len(xy_coords[0]) > 2:
        addIndex = True
        csv_lines = 'id,y,x\n'
    else:
        addIndex = False
        csv_lines = 'x,y\n'
    for line in xy_coords:
        if addIndex:
            csv_lines += str(line[0]) + ',' + str(line[2]) + ',' + str(line[1]) + '\n'
        else:
            csv_lines += str(line[0]) + ',' + str(line[1]) + '\n'
    print 'Writing csv', csv_name
    csv_open = open(csv_name, 'w')
    csv_open.writelines(csv_lines)
    csv_open.close()
########################################################################################################################
def proj_coord_to_array_coord(proj_coords, array_coord_list, res):
    xmin = array_coord_list[0]
    ymax = array_coord_list[-1]
    offsetx = int(math.floor((float(proj_coords[0]) - float(xmin))/float(res)))
    offsety = int(math.floor((float(ymax) - float(proj_coords[1]))/ float(res)))
    return [offsetx, offsety]

def array_coord_to_proj_coord(array_coords, array_coord_list, res):
    x = array_coords[0]
    y = array_coords[1]
    xoffset = math.ceil(float(x) * float(res)) + float(array_coord_list[0]) -  (0.5 * res)
    yoffset = math.ceil(float(array_coord_list[-1]) - (float(y) * float(res))) -  (0.5 * res)
    return [xoffset, yoffset]
########################################################################################################################
#Calculates the x, y coordinates of a point shapefile using the r library "maptools"
#Returns a 2-d array of the coordinates
#There is the option of producing a csv file with the coordinates as well
def xy_coords(shapefile, write_csv = False, csv_name = 'default_csv.csv', addIndex = False):
    shapeData = ogr.Open(shapefile)
    layer = shapeData.GetLayer()
    points = []
    for index in xrange(layer.GetFeatureCount()):
        feature = layer.GetFeature(index)
        geometry = feature.GetGeometryRef()
        if addIndex:
            points.append([index,geometry.GetX(), geometry.GetY()])
        else:
            points.append([geometry.GetX(), geometry.GetY()])
    out_list = points


    if write_csv == True:
        write_xy_csv(points, csv_name)
    return out_list
def shp_to_kml(in_shp, out_kml, zone = ''):
    xys = xy_coords(in_shp)
    xy_list_to_kml(xys, out_kml, zone)
def get_feature_type(shapefile):
    shp = ogr.Open(shapefile)
    lyr = shp.GetLayer()
    featList = range(lyr.GetFeatureCount())
    feat = lyr.GetFeature(featList[0])
    geom = feat.GetGeometryRef()
    return geom.GetGeometryName()
def compute_area(shapefile):
    shp = ogr.Open(shapefile)
    lyr = shp.GetLayer()
    featList = range(lyr.GetFeatureCount())

    area_list = []
    #perim_list = []
    for FID in featList:

        feat = lyr.GetFeature(FID)
            # Get extent of feat
        geom = feat.GetGeometryRef()
        area_list.append(geom.GetArea())
        #perim_list.append(geom.Length())
    return area_list#, perim_list
def xy_poly_coords(shapefile):
    shp = ogr.Open(shapefile)
    lyr = shp.GetLayer()
    featList = range(lyr.GetFeatureCount())
    ftl = []
    area_list = []
    #statDict = {}

    out_list = []
    for FID in featList:
        #print 'Extracting fid', FID
        feat = lyr.GetFeature(FID)
            # Get extent of feat
        geom = feat.GetGeometryRef()
##        area_list.append(geom.GetArea())
        #print FID,geom.GetGeometryName()
        olt = []
        if (geom.GetGeometryName() == 'MULTIPOLYGON'):
            ftl.append('MULTIPOLYGON')
            count = 0
            #pointsX = []; pointsY = []
            for polygon in geom:
                oltt = []
                geomInner = geom.GetGeometryRef(count)
                ring = geomInner.GetGeometryRef(0)
                numpoints = ring.GetPointCount()
                for p in range(numpoints):
                        lon, lat, z = ring.GetPoint(p)
                        #pointsX.append(lon)
                        #pointsY.append(lat)
                        oltt.append([lon,lat])
                olt.append(oltt)
                count += 1
        elif (geom.GetGeometryName() == 'POLYGON'):
            ftl.append('POLYGON')
            ring = geom.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            #pointsX = []; pointsY = []

            for p in range(numpoints):
                    lon, lat, z = ring.GetPoint(p)
                    olt.append([lon,lat])
                    #pointsX.append(lon)
                    #pointsY.append(lat)
        out_list.append(olt)
##    print 'Area list', area_list
    return out_list, ftl

#######################################################
#Takes a point shapefile and creates a plot kml and shp with radius specified
def point_shp_to_plot_kml(shp,kml,radius):
    proj4 = shape_info(shp)['proj4']
    xys =  xy_coords(shp, write_csv = False)
    ids = multiple_field_extraction(shp,['FID'])
    ids = map(lambda i: i[0],ids)
    out=[]
    for i in range(0,len(xys)):
        id= ids[i]
        xy = xys[i]

        x = xy[0]
        y = xy[1]

        t = [[x-radius,y-radius],
                [x-radius,y+radius],
                [x+radius,y+radius],
                [x+radius,y-radius]]

        out.append(t)
    tShp = os.path.splitext(kml)[0] + '_s.shp'

    if os.path.exists(kml) == False:
        list_to_polygon_shapefile(out, tShp, proj4)
        shape_to_kml(tShp, kml,'FID')

##################################
##shapefile = r'R:\NAFD3\timesync_setup\test_sampled_new_sample3\p035r032_1999_2009_union_lfd_use_sampled.shp'
##ftl,xyss =  xy_poly_coords(shapefile)
##i = 0
##for xys in xyss:
##
##    print ftl[i],numpy.shape(numpy.array(xys)), len(xys),numpy.array(xys).ndim
##    i += 1
##print len(xyss)
##        olt = []
##        geom = feat.GetGeometryRef()
##        ring = geom.GetGeometryRef(0)
##        points = ring.GetPointCount()
##        for p in xrange(points):
##            x,y,z = ring.GetPoint(p)
##            olt.append([x,y])
##        out_list.append(olt)
##
##    return out_list
##    shapeData = ogr.Open(shapefile)
##    layer = shapeData.GetLayer()
##    i = 1
##    out_list = []
##    for feat in layer:
##        olt = []
##        geom = feat.GetGeometryRef()
##        ring = geom.GetGeometryRef(0)
##        points = ring.GetPointCount()
##        for p in xrange(points):
##            x,y,z = ring.GetPoint(p)
##            olt.append([x,y])
##        out_list.append(olt)
##
##    return out_list
def get_coords(shapefile):
    ft= get_feature_type(shapefile)

    if ft == 'POINT':
        xys = xy_coords(shapefile, False)

        xyss = xys
        polygon = False
        ftl = ['POINT'] * len(xys)
    else:
        polygon = True
        xyss, ftl = xy_poly_coords(shapefile)


    return xyss,polygon, ftl


def coords_to_wkt(in_coords, geom_type):
    wkt = 'POLYGON  '#geom_type
    for fid in  range(len(in_coords)):
        wkt += '('
        polys = in_coords[fid]
        pi = 1
        for poly in polys[-3:-1]:
            print 'Converting poly no:', pi
            wkt += '('
            for xy in poly:
                wkt += str(xy[0]) + ' ' + str(xy[1]) + ','
                #print wkt
            wkt = wkt[:-1] + ')'
            pi += 1
        wkt += ')'
    return wkt

##coords, is_poly, geom_type =  get_coords(poly)
##wkt = coords_to_wkt(coords,geom_type[0])
##
##pt_driver = ogr.GetDriverByName("ESRI Shapefile")
##pt_dataSource = pt_driver.Open(points, 0)
##pt_layer = pt_dataSource.GetLayer()
##print pt_layer.GetFeatureCount()
##pt_layer.SetSpatialFilter(ogr.CreateGeometryFromWkt(wkt))
##print pt_layer.GetFeatureCount()
##
##
##poly_shp = ogr.Open(poly)
##lyr = poly_shp.GetLayer()
##
##pt_layer.SetSpatialFilter(lyr)

##pt_coords, types,ftl_pt = get_coords(points)

##print pt_coords

##shp= '//166.2.126.25/glrc_vct/NAFD3/timesync_setup/test_sampled_new_sample3/p035r032_1999_2009_union_lfd_use_sampled.shp'
##print get_coords(shp)
###get_feature_type(shp)
##raw_input()
def point_feature_to_array_location(xy,coords,res):
    return proj_coord_to_array_coord(xy, coords, res)
def poly_feature_to_array_location(xyss,coords,res):
    out_list = []
    #for xys in xyss:
        #print xys
    out_listx = []
    out_listy = []
    for xy in xyss:

        t= proj_coord_to_array_coord(xy, coords, res)

        out_list.append(t)
##        out_listx.append(t[0])
##        out_listy.append(t[1])
##    out_list.append([out_listx,out_listy])
    out_list = transpose(out_list)

    return out_list
def multi_poly_feature_to_array_location(xysss,coords,res):
    out_list = []
    for xyss in xysss:
        out_list.append(poly_feature_to_array_location(xyss,coords,res))
    return out_list
def coord_to_array_location(xyss, raster, ftl = ''):
    info = raster_info(raster)
    coords = info['coords']
    res = info['res']
    out_list = []
    if ftl == '':
        ftl = ['POINT'] * len(xyss)
    i = 0
    for xys in xyss:
        ft= ftl[i]
        if ft == 'POINT':
            out_list.append(point_feature_to_array_location(xys,coords,res))
        elif ft == 'POLYGON':
            out_list.append(poly_feature_to_array_location(xys,coords,res))
        elif ft == 'MULTIPOLYGON':
            out_list.append(multi_poly_feature_to_array_location(xys,coords,res))

        i += 1
    return out_list
##    if polygon:
##
##        for xys in xyss:
##
##            out_listx = []
##            out_listy = []
##            for xy in xys:
##                t= proj_coord_to_array_coord(xy, coords, res)
##
##
##                out_listx.append(t[0])
##                out_listy.append(t[1])
##            out_list.append([out_listx,out_listy])
##
##    else:
##
##        for xy in xyss:
##            t= proj_coord_to_array_coord(xy, coords, res)
##
##
##            out_list.append(t)

##    return out_list
def proj_coord_to_array_location(shapefile, raster):

    xyss, polygon, ftl = get_coords(shapefile)

    array_xyss = coord_to_array_location(xyss,raster,ftl)
    return xyss,array_xyss,polygon,ftl

##
##default_sample = 'R:/NAFD3/timesync_setup/test_sampled_new_sample3/p035r032_1999_2009_union_lfd_use_sampled_pts.shp'
##image = 'R:/NAFD3/timesync_setup/imagery/3532/refls/p35r32_2009cmp_ev_cloudfill.img'
##print proj_coord_to_array_location(default_sample,image)
##shp= 'R:/NAFD/Landtrendr/timesync2/test_data/sample/test_poly_sample.shp'
##shpp =  'R:/NAFD/Landtrendr/timesync2/test_data/sample/test_sample.shp'
##rast = 'R:/NAFD/Landtrendr/timesync2/test_data/images/p034r032_distbYear_flt_20.img'
###xy_poly_coords(shp)
##xyss = proj_coord_to_array_location(shp,rast)
##for xy in xyss:
##    print xy

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

#r = cwd +'test.jpg'
#shp = cwd + 'test.shp'
#raster_to_shapefile(r,shp)
########################################################################################################################
##############################################################
#Function to apply a mmu and convert categorized outputs to polygons for ease of use
def apply_mmu_and_convert_to_poly(in_raster, mmu):
    #Set up names
    in_raster_mmu = os.path.splitext(in_raster)[0] +'_mmu_' + str(mmu) + os.path.splitext(in_raster)[1]
    in_raster_mmu_poly = os.path.splitext(in_raster_mmu)[0] + '_poly.shp'

    #Apply mmu
    if os.path.exists(in_raster_mmu) == False:
        print 'Creating', os.path.basename(in_raster_mmu)
        gdal_sieve(in_raster, in_raster_mmu, mmu)
    else:
        print 'Already created:',os.path.basename(in_raster_mmu)

    #Convert to polygons using raster_to_shapefile function (built on gdal_polygonize)
    if os.path.exists(in_raster_mmu_poly) == False:
        print 'Converting', os.path.basename(in_raster_mmu) , 'to polygons'
        raster_to_shapefile(in_raster_mmu, in_raster_mmu_poly)
    else:
        print 'Already created:',os.path.basename(in_raster_mmu_poly)

    #Find the feature count, add the UNID field, and update the values
    si = shape_info(in_raster_mmu_poly)
    num_features = si['feature_count']


    print 'There are', num_features, 'features in', os.path.basename(in_raster_mmu_poly)
    update_field(in_raster_mmu_poly,'UNID', range(1,num_features + 1))
    update_field(in_raster_mmu_poly, 'Area',compute_area(in_raster_mmu_poly))
    #area = compute_area(in_raster_mmu_poly)
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
def new_shapefile_to_raster(in_shp,out_rast, res = 30, no_data = ''):
    try:
        out_format = format_dict[os.path.splitext(out_rast)[1]]
    except:
        out_format = 'HFA'
    # Open the data source and read in the extent
    source_ds = ogr.Open(in_shp)
    source_layer = source_ds.GetLayer()
    source_srs = source_layer.GetSpatialRef()


    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    # Create the destination data source
    x_res = int((x_max - x_min) / res)
    y_res = int((y_max - y_min) / res)
    print 'Initializing output raster:', out_rast
    target_ds = gdal.GetDriverByName(out_format).Create(out_rast, x_res, y_res, gdal.GDT_Byte)
    target_ds.SetGeoTransform((x_min, res, 0, y_max, 0, -res))
    #target_ds.SetProjection(projection)
    target_ds.SetProjection(source_srs.ExportToWkt())
    band = target_ds.GetRasterBand(1)
    if no_data != '' and no_data != None:
        band.SetNoDataValue(int(no_data))
    gdal.RasterizeLayer(target_ds, [1], source_layer, None, None, [1], ['ALL_TOUCHED=TRUE'])#burn_values=[0])
    print 'Closing raster'

def grow_raster(in_raster, out_raster,no_pixels = 100):
    ri = raster_info(in_raster)
    coords = ri['coords']
    res = ri['res']
    offset = res * no_pixels
    out_width = ri['width'] + 2*no_pixels
    out_height = ri['height'] + 2*no_pixels
    out_coords = [coords[0] - offset,coords[1] - offset,coords[2] + offset, coords[3] + offset]
    out_transform = [out_coords[0], res, 0, out_coords[-1], 0, -res]
    ti = tiled_image(out_raster, template_image = '', width = out_width, height = out_height, bands = ri['bands'], dt = ri['dt'], transform = out_transform, projection = ri['projection'],out_no_data = ri['no_data'])
    ti.add_tile(brick(in_raster),no_pixels,no_pixels)
    ti.rm()

##############################################################################################
#Will merge a list of shapefiles to a single shapefile using ogr2ogr.exe
#All shapefiles must be of the same type (point, polyline, or polygon), and projection (ogr2ogr does not support on-the-fly reprojection)
def merge_shapefile(merge_list, output_name, gdal_dir = gdal_dir):
    if os.path.exists(merge_list[0]) == True:
        if os.path.exists(output_name) == False:
            try:
                make_merge_shp = gdal_dir + 'ogr2ogr -f "ESRI Shapefile" "' + output_name + '" "' + merge_list[0] + '"'
                print make_merge_shp
                call = subprocess.Popen(make_merge_shp)
                call.wait()
            except:
                'Could not create', output_name
    else:
        print merge_list[0], 'does not exist'
    for merge in merge_list[1:]:
        merge_call = gdal_dir + 'ogr2ogr -f "ESRI Shapefile" -update -append "' + output_name + '" "' + merge + '" -nln ' + os.path.basename(os.path.splitext(output_name)[0])
        print 'Merging:', os.path.basename(merge)
        call = subprocess.Popen(merge_call)
        call.wait()
##############################################################################################
class fancy_merge_rasters:
    def __init__(self,merge_list, output_name, na_value = '', dt = '',overlap_function = 'numpy.amax', x_buffer = 50, y_buffer = 50, out_extent = [],compression = False):
        self.tilei = 1
        self.compression = compression
        self.merge_list = merge_list
        self.output_name = output_name
        self.na_value = na_value
        self.overlap_function = overlap_function
        self.x_buffer = x_buffer
        self.y_buffer = y_buffer
        self.out_extent = out_extent
        if out_extent == [] or out_extent == None or out_extent == '':
            print 'Finding union extent of images'
            extents = []
            i = 1
            for image in merge_list:
                print 'Finding extent for image', i, '/', len(merge_list)
                self.info = raster_info(image)

                #print info['proj4'], info['res']
                extents.append(self.info['coords'])
                i += 1
            extents = numpy.array(extents)

            mins = numpy.amin(extents, 0)
            maxes = numpy.amax(extents, 0)
            self.image = image
            self.full_extent = [mins[0], mins[1] - y_buffer, maxes[2] + x_buffer, maxes[3]]
        else:
            self.full_extent = out_extent
            self.image = merge_list[0]
            self.info = raster_info(self.image)
        if na_value == '' or na_value == None:
            self.na_value = self.info['no_data']
        if dt == '' or dt == None:
            self.dt = info['dt']
        else:
            self.dt= dt
        full_extent = self.full_extent
        print 'Full extent',full_extent
        info = self.info
        self.res = self.info['res']
        self.info_image = self.info['image']
        self.width = int((full_extent[2] - full_extent[0]) / info['res']) + 1
        self.height = int((full_extent[3] - full_extent[1]) / info['res']) + 1
        self.out_transform = [full_extent[0], info['res'], 0.0, full_extent[-1], 0.0, -1 * info['res']]
        self.ct, self.names, b1, rast = color_table_and_names(self.image, band = 1)
        self.merge_dict = {}
        ii = 1
        for image in self.merge_list:
##            print
##            print
##            print
##            print 'Merging image', ii, '/', len(merge_list)
##            print
            info = raster_info(image)
            xmin = info['coords'][0]
            ymax = info['coords'][-1]
            xo = int((xmin - full_extent[0]) / info['res'])
            yo = int((full_extent[-1] - ymax) / info['res'])
            self.merge_dict[image] = [xo,yo]
            #print xmin, ymax,xo,yo
            #b = brick(image, na_value = na_value)
            if ii == 1:
                oft = ''
            else:
                oft = overlap_function
            #try:
            #ti.add_tile(b, xo, yo, overlap_function = oft)
            #except:
                #print 'Could not add', image
            #b = None
            ii += 1
    def init_output(self):
        self.ti = tiled_image(self.output_name, '', self.width, self.height, bands = self.info['bands'], dt = self.dt, transform = self.out_transform, projection = self.info['projection'], df = format_dict[os.path.splitext(self.output_name)[1]], outline_tiles = True, size_limit_kb = 120000, make_output = True, ct = self.ct, names = self.names, out_no_data = self.na_value,compression = self.compression)
    def update_output(self):
        print 'Opening', os.path.basename(self.output_name) ,'to update'
        self.ti = tiled_image(self.output_name, '', self.width, self.height, bands = self.info['bands'], dt = self.dt, transform = self.out_transform, projection = self.info['projection'], df = format_dict[os.path.splitext(self.output_name)[1]], outline_tiles = True, size_limit_kb = 120000, make_output = False, ct = self.ct, names = self.names, out_no_data = self.na_value,compression = self.compression)
        #self.ti = gdal.Open(self.output_name, gdal.GA_Update)
    def update_or_init_output(self):
##        if os.path.exists(self.output_name) == False:
        self.init_output()
##        else:
##            self.update_output()
    def add_tile(self, array,image_name = '',xo = '',yo = ''):
        if image_name != '':
            xo,yo = self.merge_dict[image_name]
        if self.tilei == 1:
            oft = ''
        else:
            oft = self.overlap_function
        self.ti.add_tile(array,xo,yo, overlap_function = oft)
        self.tilei += 1
    def rm(self):
        print 'Closing', os.path.basename(self.output_name)
        self.ti.rm()
    def stats(self):
        brick_info(self.output_name,True)
##############################################################################################
def merge_rasters(merge_list, output_name, na_value = '', overlap_function = 'numpy.amax', x_buffer = 50, y_buffer = 50, out_extent = [],compression = False):
    if out_extent == [] or out_extent == None or out_extent == '':
        print 'Finding union extent of images'
        extents = []
        i = 1
        for image in merge_list:
            print 'Finding extent for image', i, '/', len(merge_list)
            info = raster_info(image)

            #print info['proj4'], info['res']
            extents.append(info['coords'])
            i += 1
        extents = numpy.array(extents)

        mins = numpy.amin(extents, 0)
        maxes = numpy.amax(extents, 0)

        full_extent = [mins[0], mins[1] - y_buffer, maxes[2] + x_buffer, maxes[3]]
    else:
        full_extent = out_extent
        image = merge_list[0]
        info = raster_info(image)
    if na_value == '' or na_value == None:
        na_value = info['no_data']
    width = int((full_extent[2] - full_extent[0]) / info['res'])# + 1
    height = int((full_extent[3] - full_extent[1]) / info['res'])# + 1
    out_transform = [full_extent[0], info['res'], 0.0, full_extent[-1], 0.0, -1 * info['res']]
    ct, names, b1, rast = color_table_and_names(image, band = 1)
    #print names
    #print width,height
    ti = tiled_image(output_name, '', width, height, bands = info['bands'], dt = info['dt'], transform = out_transform, projection = info['projection'], df = format_dict[os.path.splitext(output_name)[1]], outline_tiles = True, size_limit_kb = 120000, make_output = True, ct = ct, names = names, out_no_data = na_value,compression = compression)
    ii = 1
    for image in merge_list:
        print
        print
        print
        print 'Merging image', ii, '/', len(merge_list)
        print
        info = raster_info(image)
        xmin = info['coords'][0]
        ymax = info['coords'][-1]
        xo = int((xmin - full_extent[0]) / info['res'])
        yo = int((full_extent[-1] - ymax) / info['res'])
        print xmin, ymax,xo,yo
        b = brick(image)#, na_value = na_value)

        if ii == 1:
            oft = ''
        else:
            oft = overlap_function

##        if na_value != '' and na_value != None:
##                #print 'Masking no data value:', no_data
##                #print 'Numpy dt:', numpy_dt
##                #br.ReadAsArray(xo, yo, a_width, a_height).astype(numpy_dt)
##                msk = numpy.equal(b,na_value)
##                #print 'msk',msk
##                #print 'msk_shp',msk.shape
##                #print 'at_shp', at.shape
##                #print 'from_array_shp', from_array.shape
##                numpy.putmask(b,msk,from_array)
        #try:
        ti.add_tile(b, xo, yo, overlap_function = oft)
        #except:
            #print 'Could not add', image
        b = None
        ii += 1
    print
    print
    print 'Closing out', output_name
    ti.rm()
##folder = 'X:/Landsat_Mosaics/r_numpy_method_test/'
##images = glob(folder, '.img')
##out = folder + 'out/out_test3.img'
##merge_rasters(images[:-1], out)
##############################################################################################
def gdal_merge(merge_list, output_name,gdal_dir = gdal_dir):
    bat_lines = 'c:\ncd ' + gdal_dir + '\n'
    #if clip_extent != '' and clip_extent != None:


    call = 'gdal_merge.py -o ' + output_name + ' -q -v -of ' + format_dict[os.path.splitext(output_name)[1]]
    for image in merge_list:
        call += ' "' + image+'" '
    call = call[:-1]
    bat_lines += call
    bat_lines += '\n' + cwd[:2]
    print bat_lines
    bat_dir = os.path.dirname(output_name) + '/bat_files/'
    check_dir(bat_dir)
    bat_file = bat_dir + base(output_name) +'_merge.bat'
    bo = open(bat_file, 'w')
    bo.writelines(bat_lines)
    bo.close()

    c = subprocess.Popen(bat_file)
    c.wait()


##############################################################################################
def shp_mbr_to_raster(in_shp, out_rast, template_rast, rast_value = 1, resolution = 30, dt = 'Byte'):
    shp_info = shape_info(in_shp)
    in_coords = shp_info['coords']

    ulx = in_coords[0]
    uly = in_coords[-1]

    width = abs(int(math.ceil((in_coords[0] - in_coords[2]) / float(resolution))))
    height = abs(int(math.ceil((in_coords[-1] - in_coords[1]) / float(resolution))))
    print 'width', width
    print 'height', height
    tform = [in_coords[0], resolution, 0.0, in_coords[1], 0.0, resolution]
    print 'Transform', tform
    print 'Projection', shp_info['projection']
    if numpy_or_gdal(dt) == 'gdal':

        dtn = dt_converter(dt)
    else:
        dtn = dt
    r = numpy.zeros([height, width]).astype(dtn)

    r[r == 0] = rast_value
    write_raster(r, out_rast, template_rast,dt = dt, width = width, height = height, transform = tform)
    print r
    r = None
    del r

#in_shp = 'X:/Landsat/169067/subset/subset_169067.shp'
#out_raster = 'X:/Landsat/169067/landtrendr/mask/169067_msk2.img'
#template_rast = 'X:/Landsat/169067/landtrendr/mask/p169r067_commMask'
#shp_mbr_to_raster(in_shp, out_raster, template_rast)
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
def add_field(shapefile, field_name, datatype = 'Integer',fieldWidth = 25):
    if len(field_name) > 10:
        field_name = field_name[:10]
    field_name = field_name.upper()
    source = ogr.Open(shapefile, 1)
    layer = source.GetLayer()
    layer_defn = layer.GetLayerDefn()
    field_names = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]
    print 'Currently existing field names are:', field_names
    if field_name not in field_names:
        print 'Adding field name: ', field_name
        new_field = ogr.FieldDefn(field_name, eval('ogr.OFT' + datatype))
        print 'Setting field width'
        new_field.SetWidth(24)
        print 'Finished setting width'
        layer.CreateField(new_field)
    else:
        print field_name, 'already exists'
    source.Destroy()
########################################################################################################################
#Updates a field within a shapefile with a provided list of values
#The list of values must be of the same type as the field (list of strings for a string field type....)
#The list of values must have the same number of entries as there are features within the shapefile
def update_field(shapefile, field_name, value_list,datatype = 'Integer',fieldWidth = 25):
    if len(field_name) > 10:
        field_name = field_name[:10]
    print 'Shortened field name:',field_name
    updated = False
    while updated == False:
        try:
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

            updated = True
        except:
            db1.close()
            add_field(shapefile,field_name,datatype,fieldWidth)

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
def extract_xy_value(in_raster_object, x,y,band = 1, c_dt = 'f',dt = 'Float32'):
    import struct

    rb = in_raster_object.GetRasterBand(band)
    try:
        raster_value = rb.ReadRaster(x, y, 1, 1, buf_type = eval('gdal.GDT_Int16'))#' + dt))#' + ri['dt']))
        value = struct.unpack(c_dt, raster_value)[0]
    except:
        try:
            raster_value = rb.ReadRaster(x, y, 1, 1, buf_type = eval('gdal.' + dt))#' + ri['dt']))
            value = struct.unpack(c_dt, raster_value)[0]
        except:
            value = 0
    rb = None
    return value
#Equivalent function as extract_value_to_list, but does not use R
def epv(in_point_shp, in_raster, band = 1):
    import struct
    out_list = []
    #Extract coordinates from shapefile
    xys = xy_coords(in_point_shp, False)
    gdal_dt_to_c_dt = {
        'Float32' : 'f',
        'Float64' : 'f',
        'Byte': 'H',
        'UInt16':'h',
        'Int16':'H'}
    #Get the raster info
    ri = raster_info(in_raster)
    dt = ri['dt']

    if numpy_or_gdal(dt) == 'numpy':

        dt = dt_converter(dt)
    try:
        c_dt = gdal_dt_to_c_dt[dt]
    except:
        c_dt = 'f'

    raster_coord_list = []

    #Set up a raster object
    src_ds = gdal.Open(in_raster)

    rb = src_ds.GetRasterBand(band)
    eoffset = 0
    print 'Extracting', len(xys), 'values from', in_raster
    current_index = 0
    list_length = len(xys)
    last = 0
    for xy in xys:
        #print xy
        #Convert shape coord to raster coordinate
        raster_coords = proj_coord_to_array_coord(xy, ri['coords'], ri['res'])

        #Extract raster value
        try:
            raster_value = rb.ReadRaster(raster_coords[0]-eoffset, raster_coords[1]-eoffset, 1, 1, buf_type = eval('gdal.GDT_Int16'))#' + dt))#' + ri['dt']))
            value = struct.unpack(c_dt, raster_value)[0]
        except:
            try:
                raster_value = rb.ReadRaster(raster_coords[0]-eoffset, raster_coords[1]-eoffset, 1, 1, buf_type = eval('gdal.' + dt))#' + ri['dt']))
                value = struct.unpack(c_dt, raster_value)[0]
            except:
                value = -9999
        #print value
        out_list.append(value)
        last = status_bar(current_index, list_length, percent_interval = 5,last = last)
        current_index += 1
    return out_list
    #return [1,2]
def epv_brick(in_point_shp, in_raster, bands = []):
    if bands == [] or bands == '' or bands == None:
        ri= raster_info(in_raster)
        bands = range(1, ri['bands'] + 1)
    out_list = []
    for band in bands:
        print 'Extracting values from band:',band
        out_list.append(epv(in_point_shp,in_raster, band))
    out_list = transpose(out_list)
    return out_list

def bat_single_epv(x,y, images, bands = 'All'):
    #Get the raster info


    out_list = []
    for image in images:
        ri = raster_info(images[0])
        dt = ri['dt']
        gdal_dt_to_c_dt = {
            'Float32' : 'f',
            'Float64' : 'f',
            'Byte': 'H',
            'UInt16':'h',
            'Int16':'H'}
        if numpy_or_gdal(dt) == 'numpy':

            dt = dt_converter(dt)
        try:
            c_dt = gdal_dt_to_c_dt[dt]
        except:
            c_dt = 'f'
        if bands == 'All':
            bands = range(1,ri['bands'] + 1)
        #print 'Extracting value',x,y, 'from', base(image)
        tl = []
        #Set up a raster object
        src_ds = gdal.Open(image)
        #tl= list(brick(image,'',x,y,1,1).flatten())
        for band in bands:

            tl.append(extract_xy_value(src_ds,x,y,band,c_dt,dt))
        out_list.append(tl)
    src_ds = None
    return out_list

##s = 'R:/NAFD3/timesync_setup/test_sampled_new_sample3/p035r032_1999_2009_union_lfd_use_sampled_pts.shp'
##images = glob('R:/NAFD3/timesync_setup/imagery/3532/refls/','.img')
##ri = raster_info(images[0])
##xys = xy_coords(s, False)
##rcs = proj_coord_to_array_coord(xys[50], ri['coords'], ri['res'])
##x = rcs[0]
##y = rcs[1]
##print x,y
##t1 = time.time()
##bat_single_epv(x,y, images)
##t2 = time.time()
##print t1-t2


##for image in images:
##    print epv_brick(s,image)
def epv_single(x,y, in_raster, band = 1,convert_to_raster_coords = False):
    xy=[x,y]
    #Set up a raster object
    src_ds = gdal.Open(in_raster)
    rb = src_ds.GetRasterBand(band)


    if convert_to_raster_coords:
        #Convert shape coord to raster coordinate
        raster_coords = proj_coord_to_array_coord(xy, ri['coords'], ri['res'])
    else:
        raster_coords = xy
        #Extract raster value
        try:
            raster_value = rb.ReadRaster(raster_coords[0]-1, raster_coords[1], 1, 1, buf_type = eval('gdal.GDT_Int16'))#' + dt))#' + ri['dt']))
            value = struct.unpack(c_dt, raster_value)[0]
        except:
            try:
                raster_value = rb.ReadRaster(raster_coords[0]-1, raster_coords[1], 1, 1, buf_type = eval('gdal.' + dt))#' + ri['dt']))
                value = struct.unpack(c_dt, raster_value)[0]
            except:
                value = 0
        #print value

    return value
########################################################################################################################
#Equivalent function to extract_value_to_shapefile, but does not use r
def epv_to_shp(in_point_shp, in_raster, field_name, band = 1, datatype = 'Real'):
    print 'Extracting values from', base(in_raster), 'to', base(in_point_shp)
    values = epv(in_point_shp, in_raster, band)

    try:
        update_field(in_point_shp, field_name, values)
    except:
        add_field(in_point_shp, field_name,datatype = datatype)
        update_field(in_point_shp, field_name, values)
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
source1 = '//166.2.126.214/Data/National/Terrain/NED/grid/'
source2 = '//166.2.126.214/ned13/grid/'
def dem_clip(extent_raster, output, dem_source = source2,
             res = '10', zone = '18', datum = 'WGS84', Buffer = 1000, create_mosaic = True, mask_output = True,
             dt = '', n_s_hemisphere = 'n', e_w_hemisphere = 'w', image_prefix = 'grd', overwrite = False):
    try:
        os.listdir(dem_source)
    except:
        print 'Please log onto:', dem_source
        raw_input('Press enter to continue')
    if os.path.splitext(extent_raster)[1] == '.shp':
        info = shape_info(extent_raster, False, small = True)
        cutline = extent_raster
    else:
        info = raster_info(extent_raster)
        cutline = ''
    zone =  float(info['zone'])
    coords = info['coords']
    coords = buffer_coords(coords, Buffer)
    gdal_coords = coords_to_gdal(coords)
    print zone
    print gdal_coords
    res = str(res)
    lat_lon_max =  utm_to_geog(zone, coords[0], coords[3])
    lat_lon_min = utm_to_geog(zone, coords[2], coords[1])
    print 'min',lat_lon_min
    print 'max',lat_lon_max

    lat_range = range(math.floor(float(lat_lon_min[0])), math.ceil(float(lat_lon_max[0])) + 1)
    lon_range = range(abs(math.ceil(float(lat_lon_min[1]))), abs(math.floor(float(lat_lon_max[1]))) + 1)
    geog_coords_str = str(float(lat_lon_max[1])) + ', ' + str(float(lat_lon_min[0])) + ', ' + str(float(lat_lon_min[1])) + ', ' + str(float(lat_lon_max[0]))
    geog_coords = [str(float(lat_lon_max[1])) , str(float(lat_lon_min[0])), str(float(lat_lon_min[1])) , str(float(lat_lon_max[0]))]
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
    if mask_output == True and cutline == '':
        temp_dir =os.path.dirname(output) + '/temp/'
        if os.path.exists(temp_dir) == False:
            os.makedirs(temp_dir)
        temp = temp_dir + os.path.splitext(output)[0].split('/')[-1]  + '_unclipped.img'

    else:
        temp = output

    if create_mosaic == True:
        if os.path.exists(temp) == False:

            reproject(image_list, temp, clip_extent = gdal_coords, dt = dt, res = res, zone = zone, datum = datum, resampling_method = 'cubic', cutline = cutline)


        if mask_output == True and cutline == '':
            mask_rast = extent_raster
            if os.path.exists(output) == False:
                info = raster_info(temp)
                mask(temp, mask_rast, output, dt = info['dt'], overwrite = overwrite)
    return image_list, coords, geog_coords_str
########################################################################################################################
#Algorithm outlined in: McCune and Keon, 2002
#http://people.oregonstate.edu/~mccuneb/radiation.htm
def heatload(slope,aspect, latitude = 45):

    rl = numpy.radians(latitude)
    rs = numpy.radians(slope)
    ra = numpy.radians(aspect)
    fa1 = numpy.pi-numpy.abs(ra-numpy.pi)
    fa2 = numpy.abs(numpy.pi - numpy.abs(ra - (numpy.pi *5/4))) #  ABS(PI()-ABS($F7-PI()*5/4))

    return numpy.exp(0.339+ 0.808* numpy.cos(rl) * numpy.cos(rs) - 0.196*numpy.sin(rl) - 0.482*numpy.cos(fa2)*numpy.sin(rs))
########################################################################################################################
#Calculates several terrain derivatives from a provided DEM using the gdaldem.exe program
def dem_derivatives(dem, out_dir = '', gdal_dir = gdal_dir, derivative_list = ['slope', 'aspect', 'roughness', 'hillshade', 'TPI', 'TRI'], overwrite = False, compute_stats = True, latitude = 45):
    deriv_list = []
    other_derivatives = ['heatload']
    main_derivatives =  ['slope', 'aspect', 'roughness', 'hillshade', 'TPI', 'TRI']
    slope_name = ''
    aspect_name = ''
    ri = raster_info(dem)
    #print dem
    if out_dir != '' and out_dir != None:
        check_dir(out_dir)
    for derivative in derivative_list:

        if out_dir != '' and out_dir != None:
            output = out_dir + base(dem) + '_'+derivative+'.img'
        else:
            output = os.path.splitext(dem)[0] + '_'+derivative+'.img'
        if derivative == 'slope':
            slope_name = output
        if derivative == 'aspect':
            aspect_name = output
        if derivative not in other_derivatives and derivative in main_derivatives:
            if os.path.exists(output) == False or overwrite == True:
                print 'Computing: ', derivative
                gdal_call = gdal_dir + 'gdaldem '+derivative+' -of HFA ' + dem + ' ' + output
                print gdal_call
                call = subprocess.Popen(gdal_call)
                call.wait()
                print
            if compute_stats:
                raster_info(output, 1, True)
        elif derivative in other_derivatives and slope_name != '' and aspect_name != '':


            ti = tiled_image(output,dem,outline_tiles = True,make_output = True, size_limit_kb = 30000, out_no_data = ri['no_data'])
            i = 1
            for xo,yo,w,h in ti.chunk_list:
                print 'Computing', derivative, 'on tile', i, '/', len(ti.chunk_list)
                print 'Latitude:', latitude
                #d = raster(dem,'',1,xo,yo,w,h)
                a = raster(aspect_name,'',1,xo,yo,w,h)
                s = raster(slope_name,'',1,xo,yo,w,h)

                exec('out ='+derivative+'(s,a,latitude)')
                a,s = None,None
                d = raster(dem,'',1,xo,yo,w,h)
                out[d == ri['no_data']] = ri['no_data']
                ti.add_tile(out, xo,yo)

                d = None
                i += 1
            ti.rm()
            raster_info(output, 1,True)
        deriv_list.append(output)
    return deriv_list
##in_dir ='W:/03_Data-Archive/02_Inputs/Terrain_Data/GEE_DEM_Test/tiles/DEM_tile_1/'
##dem  = in_dir + 'DEM_tile_1.elevation.tif'
##dem_derivatives(dem, in_dir)
#in_dir = 'W:/03_Data-Archive/03_Process/Tech_Transfer/2Predictor_Data/2Climate_Data/3Climate_Over_Sampling_demo2/2Predictors/'
#dem= in_dir + 'Flathead_DEM_Test1_proj.img'
#out_dir = in_dir + 'test/'
#print heatload(30.,180.,40.)
#dem_derivatives(dem,out_dir,derivative_list = ['slope','aspect','hillshade', 'heatload'], latitude = 45)
######################################################################################
def nlcd_clip(extent_raster, output, nlcd_source = '//166.2.126.25/rseat/Programs/RSSC/fy2012/Projects/10025_R&D_Thermal_Mapping/02_Data-Archive/02_Inputs/Ancillary/Rasters/nlcd2006_landcover_2-14-11.img', proj = '', datum = '', res = '', zone = '', resampling_method = 'near', mask_output = True, overwrite = False, mask_method = 'mult'):
    info = raster_info(extent_raster)
    proj4_source = raster_info(nlcd_source)['proj4']
    if res == '':
        res = info['res']

    if zone == '':
        zone = info['zone']

    coords = info['gdal_coords']
    if info['proj4'] != proj4_source:
        crs = info['proj4']
    else:
        crs = ''
    print crs

    if mask_output == True:
        temp_dir =os.path.dirname(output) + '/temp/'
        if os.path.exists(temp_dir) == False:
            os.makedirs(temp_dir)



        temp = temp_dir + os.path.splitext(output)[0].split('/')[-1]  + '_unclipped.img'
    else:
        temp = output
    reproject(nlcd_source, temp, clip_extent = coords, crs = crs, res = res, resampling_method = resampling_method)
    if mask_output == True:
        if os.path.exists(output) == False:
            info = raster_info(temp)
            mask(temp, extent_raster, output, dt = info['dt'], overwrite = overwrite, mask_method = mask_method)
######################################################################################
#Clips by shapefile or raster
def clip_by_shapefile(shapefile, raster, output, resampling_method = 'cubic', res = 10, mask = True, dt = 'Float32', no_data = 'NoData'):
    if os.path.splitext(shapefile)[1] != '.shp':
        info = raster_info(shapefile)
    else:
        info = shape_info(shapefile)
    proj4 = info['proj4']
    coords = info['gdal_coords']
    if mask:
        cutline = shapefile
    reproject(raster, output, crs = proj4, resampling_method = resampling_method, clip_extent = coords, res = res, cutline = cutline, dt = dt, no_data = no_data)

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
def getSpatialReferenceFromProj4(proj4):
    'Return GDAL spatial reference object from proj4 string'
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromProj4(proj4)
    return spatialReference
######################################################################################
#Converts a list of x,y coordinates to a shapefile
#Snaps the location to the centroid of a snap raster's pixel locations
def list_to_point_shapefile(xy_coord_list, snap_raster = '', output = '', prj = '',dt = 'Byte',addXY = True):
##    print 'Creating', output.split('/')[-1]
    if snap_raster != '':
        info = raster_info(snap_raster)
        projection = info['projection']
        proj4 = info['proj4']
    elif prj !='':
        projection = prj
        proj4 = prj
    if os.path.exists(output):
        delete_shapefile(output)
    #Project it
    prj = os.path.splitext(output)[0] + '.prj'
    if os.path.exists(projection) == True:
        shutil.copy(projection, prj)
    else:
        prj_open = open(prj, 'w')
        prj_open.writelines(projection)
        prj_open.close()


    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapePath = output
    shapeData = driver.CreateDataSource(shapePath)
    spatialReference = getSpatialReferenceFromProj4(proj4)
    layerName = os.path.splitext(os.path.basename(shapePath))[0]


    layer = shapeData.CreateLayer(layerName, spatialReference, ogr.wkbPoint)
    layerDefinition = layer.GetLayerDefn()

    pointIndex = 0
    xs = []
    ys = []
    for xy in xy_coord_list:
        geometry = ogr.Geometry(ogr.wkbPoint)
        geometry.SetPoint(0, xy[0], xy[1])
        feature = ogr.Feature(layerDefinition)
        feature.SetGeometry(geometry)
        feature.SetFID(pointIndex)
        layer.CreateFeature(feature)
        geometry.Destroy()
        feature.Destroy()
        pointIndex += 1
        xs.append(xy[0])
        ys.append(xy[1])
    shapeData.Destroy()



    #add_field(output, 'x', datatype = 'Real')
    #add_field(output, 'y', datatype = 'Real')
    if addXY:
        update_field(output, 'XS', xs, datatype = 'Integer',fieldWidth =25)
        update_field(output, 'YS', ys, datatype = 'Integer',fieldWidth =25)
######################################################################################
def list_to_polygon_shapefile(xy_coord_list, output, proj4):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapePath = output
    shapeData = driver.CreateDataSource(shapePath)
    spatialReference = getSpatialReferenceFromProj4(proj4)
    layerName = os.path.splitext(os.path.basename(shapePath))[0]
    layer = shapeData.CreateLayer(layerName, spatialReference, ogr.wkbPolygon)

    if numpy.ndim(xy_coord_list) == 2:
        xy_coord_lists = [xy_coord_list]
    else:
        xy_coord_lists = xy_coord_list

    for xy_coord_list in xy_coord_lists:
##        print xy_coord_list
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for vertex in xy_coord_list:
            ring.AddPoint(vertex[0], vertex[1])
        if xy_coord_list[0] != xy_coord_list[-1]:
            ring.CloseRings()

        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetGeometry(poly)
        layer.CreateFeature(feature)
    feature.Destroy()
    shapeData.Destroy()
#Taken from: http://geospatialpython.com/2011/01/point-in-polygon.html
def point_in_poly(x,y,poly):

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside
######################################################################################
#Wrapper to find points that intersect set of polygons
def intersectPoints(points,polygons,output):
    out_xys = []
    xys = xy_coords(points, False)

    coordss,Type = xy_poly_coords(polygons)
    current_index = 0
    list_length = len(xys)
    last = 0

    for x,y in xys:
        intersects = False
        ci = 0
        while intersects == False and ci < len(coordss):

            intersects =point_in_poly(x,y,coordss[ci])
            ci += 1
        if intersects:
            out_xys.append([x,y])
        last = status_bar(current_index, list_length, percent_interval = 1, last = last)
        current_index += 1
    list_to_point_shapefile(out_xys, snap_raster = '', output =  output, prj = crs,dt = 'Long',addXY = False)


######################################################################################
def degreeTileMaker(output,size = 10,proj4 = '+proj=longlat +datum=NAD83 +no_defs'):


    xs = range(-180,171,size)
    ys = range(-90,81,size)[::-1]

    xys = []
    tiles = []
    for x in xs:
        for y in ys:
            xys.append([x,y])
    lonField = []
    latField = []
    lonLatField = []
    for xy in xys:
        t = [[xy[0],xy[1]],
            [xy[0]+size,xy[1]],
            [xy[0]+size,xy[1]-size],
            [xy[0],xy[1]-size]
            ]
        lonField.append(xy[0])
        latField.append(xy[1])
        lonLatField.append(str(xy[0]) + '_' + str(xy[1]))
        tiles.append(t)

    print output
    if os.path.exists(output) == False:
        list_to_polygon_shapefile(tiles, output, proj4)

        update_field(output, 'lon', lonField,datatype = 'Integer')
        update_field(output, 'lat', latField,datatype = 'Integer')
        update_field(output, 'lonLat',lonLatField, datatype = 'String')
    else:
        print 'Already created',output
######################################################################################
def mbr_coords(coords):
    out_coords = []

    ulxy = [coords[0], coords[-1]]
    urxy = [coords[2], coords[-1]]
    llxy = [coords[0], coords[1]]
    lrxy = [coords[2], coords[1]]
    out_coords = [ulxy, urxy, lrxy, llxy, ulxy]

    return out_coords
######################################################################################
def polygon_to_mbr_polygon(Input, Output):
    info = shape_info(Input)
    coords = info['coords']
    out_coords = mbr_coords(coords)
    if os.path.exists(Output) == False:
        print 'Creating mbr polygon:', Output
        list_to_polygon_shapefile(out_coords, Output, info['proj4'])
    else:
        print 'Already created:', Output

######################################################################################
def big_ndi(in_stack, output, band1, band2, ratio= False):
    ti = tiled_image(output,in_stack,dt = 'Float32',bands = 1, outline_tiles = True)

    ci = 1
    for xo,yo,w,h in ti.chunk_list:

        print 'Processing chunk:', ci,'/' + str(len(ti.chunk_list))
        r1 = raster(in_stack,'Float32',band1,xo,yo,w,h)
        r2 = raster(in_stack,'Float32',band2,xo,yo,w,h)

        if ratio:
            out = r1/r2
        else:
            out = (r1 - r2) / (r1 + r2)
        print out.dtype
        ti.add_tile(out,xo,yo)

        out = None
        r1 = None
        r2 = None
        ci += 1

    ti.rm()
######################################################################################
#Computes a normalized difference index for a stack
#Some common Landsat TM ndi's are:
#ndvi: band1 = 4, band2 = 3
#nbr: band1 = 4, band2 = 6 (or 7 if TIR is left in the stack) (default)
#vig: band1 = 2, band2 = 3
#ndmi: band1 = 4, band2 = 5
def ndi(stack1, output, band1 = 4, band2 = 6, clip_raster = '', overwrite = False, mask_rast = '', mask_in_value = -9999, mask_out_value = -9999):
    if os.path.exists(output) == False or overwrite == True:
        print
        print
        print 'Computing:', os.path.basename(output)
        print 'Using bands:', band1, band2
        if type(stack1) == list:
            b1 = raster(stack1[band1 - 1], dt = 'Float32')
            b2 = raster(stack1[band2 - 1], dt = 'Float32')
            stack_t = stack1[band1 - 1]
        else:
            b1 = raster(stack1, dt = 'Float32', band_no = band1)
            b2 = raster(stack1, dt = 'Float32', band_no = band2)
            stack_t = stack1
        index = ((b1 - b2) / (b1 + b2)) * 1000.0
        #index[(b1 + b2) == 0.0] = 0.0
        print 'yay'
        if mask_rast != '':
            mr = raster(mask_rast)
            index[mr == mask_in_value] = mask_out_value
            mr = None
        if clip_raster != '':
            mask(index, clip_raster, output, dt = 'Int16')
        else:
            write_raster(index, output, stack_t, dt = 'Int16')
            raster_info(output, get_stats = True)
        b1 = None
        b2 = None
        index = None
    else:
        print output, 'already exists'
########################################################################################################################
def tc(toa_mosaics, indices_dir, mask_rast = '', mask_in_value = -9999, mask_out_value = -9999, band_list = [1,2,3,4,5,7], tm_or_etm = 'tm'):

    #toa_mosaics = glob_end(mosaic_dir, '_toa_masked_mosaic.img')
    #Huang 2003
    tc_coeffs_etm = [['brightness', '0.356121', '0.397229', '0.390404', '0.696586', '0.228628', '0.159591'],
                ['greenness', '-0.334388', '-0.354442', '-0.45558', '0.6966020', '-0.0242135', '-0.262986'],
                ['wetness', '0.262619', '0.214067', '0.0926052',  '0.0656017', '-0.762868', '-0.5388500']]
    #Crist 1985
    tc_coeffs_tm = [['brightness', '0.2043', '0.4158', '0.5524', '0.5741', '0.3124', '0.2303'],
                    ['greenness', '-0.1603', '-0.2819', '-0.4934', '0.7940', '-0.0002', '-0.1446'],
                    ['wetness', '0.0315', '0.2021', '0.3102', '0.1594', '-0.6806', '0.6109']]

    if tm_or_etm == 'tm':
        tc_coeffs = tc_coeffs_tm
    else:
        tc_coeffs = tc_coeffs_etm
    out_list = []
    for tm in toa_mosaics:
        out_list_t = []
        for index in tc_coeffs:
            out = indices_dir + os.path.splitext(os.path.basename(tm))[0] + '_' + index[0] +'.img'
            if os.path.exists(out) == False:
                print 'Computing', index[0]
                br = raster(tm, 'Float32', 1)
                br = br * float(index[1])
                i = 2
                for coeff in index[2:]:
                    rt = raster(tm, 'Float32', band_list[i -1]) * float(index[i])
                    br = br + rt
                    rt = None
                    del rt
                    i += 1

                if mask_rast != '':
                    mr = raster(mask_rast)
                    br[mr == mask_in_value] = mask_out_value
                    mr = None
                write_raster(br, out, tm, dt = 'Int16')
                raster_info(out, get_stats = True)
                print
                print
                br = None
                del br
            out_list_t.append(out)
        out_list.append(out_list_t)
    return out_list
########################################################################################################################
#A function that produces several common indices using the ndi function
#Can specify a different band_dict if the bands are of a different sensor
#Comb_dict should remain the same regardless of the sensor
def index_maker(stack1, output_dir, clip_raster = '', band_dict = {'blue': 1, 'green' : 2, 'red' : 3, 'nir' : 4, 'swir1' : 5, 'tir' : 6, 'swir2' : 7}, index_list = ['nbr','ndvi', 'vig','ndmi', 'ndsi'], run_tc = True, overwrite = False, mask_rast = '', mask_in_value = -9999, mask_out_value = -9999):
    tc_list = ['brightness', 'greenness', 'wetness']
    if type(stack1) == list:
        stack_base = stack1[0]
    else:
        stack_base = stack1
    comb_dict = {'nbr': [band_dict['nir'],band_dict['swir2']],
                'ndvi': [band_dict['nir'],band_dict['red']],
                 'vig': [band_dict['green'],band_dict['red']],
                 'ndmi': [band_dict['nir'],band_dict['swir1']],
                 'ndsi' : [band_dict['nir'], band_dict['tir']]
                 }
    if run_tc:
        tc([stack1], output_dir, mask_rast, mask_in_value, mask_out_value)
    for index in index_list:

        output = output_dir + base(stack_base)+ '_' + index + '.img'
        print 'Creating', output
        ndi(stack1, output, comb_dict[index][0], comb_dict[index][1], clip_raster, overwrite = overwrite, mask_rast = mask_rast, mask_in_value = mask_in_value, mask_out_value = mask_out_value)

########################################################################################################################
def raster_xy_to_proj_xy(x,y,coords,res):
    x_coord = (int(x)* res) + int(coords[0]) + (0.5 * res)
    y_coord = int(coords[3])- (int(y)* res) - (0.5 * res)
    return x_coord, y_coord
########################################################################################################################
#Provides similar functionality to the statified_sampler function
#Intended for larger rasters, but will work fine on any sized raster
#It makes no assumptions about the no data value
#Instead the user provides a dictionary of sample numbers
#Ex: sample_nos = {1:500, 2: 1000, 5: 750} would yield 500 samples where the raster equals 1,
#1000 samples where it equals 2, and 750 samples where it equals 5
#Very very large rasters may still run into memory errors
def big_stratified_sampler(image, sample_nos, sample_name, dt = '', wo_replacement = False, shuffle_out = True):

    #Set up some stuff
    out_shp = os.path.splitext(sample_name)[0] + '.shp'
    class_codes = sample_nos.keys()
    class_codes.sort()

    #Get the raster info for use later
    r_info = raster_info(image)
    res = r_info['res']
    coords = r_info['coords']
    print dt
    #Read in the raster as a numpy array
    r = raster(image, dt = dt)

    #Initialize the report for the sample
    if wo_replacement:
        w_replacement_str = 'without replacement'
    else:
        w_replacement_str = 'with replacement'
    rep_lines = 'Stratified Random Sample Report for: ' + image + '\nSample drawn on:' + now()+ '\n'
    rep_lines += 'Sampling was performed: ' + w_replacement_str + '\n\nSample_Class_Code\tSample_Number\n'

    #Set up a list to populate with sample coordinates
    out_list = []
    #Iterate through each class code provided
    for class_code in class_codes:
        #Find the sample number
        sample_no = sample_nos[class_code]


        #Convert the raster cells from the class that is being sampled into two numpy arrays with the coordinates
        coord_set = numpy.where(r == class_code)

        #Find the length of the list of raster coordinates for the given class
        l = len(coord_set[0]) -1

        if l > 0:
            print 'Sampling class:', class_code
            #Draw the sample with or without replacement
            if wo_replacement:
                #Check to make sure that the sample number is not larger than the population
                if l < sample_no:
                    sample_no = l
                    print 'Adjusted sample number for class:', class_code, 'to', sample_no
                st = random.sample(range(l), sample_no)
            else:
                st = numpy.random.random_integers(0, l, sample_no)

            #Update the report with the number of samples drawn for the class
            rep_lines += str(class_code) + '\t' + str(len(st)) + '\n'

            #Populate the out_list with the sampled coordinates and class from which it was sampled
            for s in st:
                so = [coord_set[0][s], coord_set[1][s], class_code]
                out_list.append(so)
            coord_set = None
        else:
            print 'No pixels to sample in class:', class_code

    #Provides the capability to shuffle the coordinates so the classes are not clumped
    if shuffle_out:
        numpy.random.shuffle(out_list)
    #Delete the raster from memory
    r = None

    #Write out the report
    sample_total = len(out_list)
    print 'Total samples:', sample_total
    rep_name = os.path.splitext(out_shp)[0] + '_sample_report.txt'
    rep_lines += 'Sample total: ' + str(sample_total)
    rlo = open(rep_name, 'w')
    rlo.writelines(rep_lines)
    rlo.close()

    #Convert the raster coordinates to projected coordinates using the raster extent and resolution
    i = 0
    class_list = []
    xy_coords = []
    for o in out_list:
        x_coord, y_coord = raster_xy_to_proj_xy(o[1], o[0], coords, res)
        class_list.append(o[-1])
        xy_coords.append((x_coord, y_coord, i + 1))
        i += 1

    #Write the xy projected coords to a shapefile
    list_to_point_shapefile(xy_coords, image, out_shp)
    #Add the class field and update it
    class_field_name = 'Cls'
    #add_field(out_shp, class_field_name, 'Integer')
    update_field(out_shp, class_field_name, class_list)
######################################################################################################
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
def inside(point_coords, rect_coords):
    i = False
    if point_coords[0] > rect_coords[0] and point_coords[0] < rect_coords[2] and point_coords[1] > rect_coords[1] and point_coords[1] < rect_coords[3]:
        i = True
    return i
def intersects(coords1, coords2, runs = 1):

    i = False
    corners = [[coords1[0], coords1[1]], [coords1[2], coords1[3]], [coords1[0], coords1[3]], [coords1[2], coords1[1]]]
    for corner in corners:
        i = inside(corner, coords2)
    if i == False and runs > 0:

            runs = runs - 1
            i = intersects(coords2, coords1, runs = runs)
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
            ot = str(directory) + '/' + str(Dir)
            if os.path.isdir(ot):
                out_list.append(ot)
            walker(directory + '/' + Dir, out_list, levels)
            levels = levels - 1
    else:

        global walker_dirs
        walker_dirs = out_list

#This function searches through a list of directories for a list of key words
#A dictionary is returned with the key word as the key and its respective directory as the definition
#Only one directory is assigned to each key- the first directory found containing the key
def nas_dir_getter(key_list = ['Minnesota', 'Michigan', 'Wisconsin'], nas_list = ['//166.2.126.33/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/',
                                                                                  '//166.2.126.23/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/',
                                                                                  '//166.2.126.19/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/'], dir_levels = 4):
    key_count = len(key_list)
    out_dict = []


    for nas in nas_list:
        print nas
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
    print out_dict
                    #if len(out_dict) == len(key_list):

    return dict(out_dict)
#########################################################################
def is_grid(file_path, standard_ext = '.adf'):
    if os.path.isdir(file_path):
        Files = os.listdir(file_path)
        for File in Files:
            if os.path.splitext(File)[1] == standard_ext:
                return True
    return False
###########################################################################
#This function combines the functions above
#This function should be used when finding NAIP directories on the NAS
def get_doqq_dirs(key_list = ['Minnesota', 'Michigan', 'Wisconsin'], nas_list = ['//166.2.126.33/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/',
                                                                                 '//166.2.126.23/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/',
                                                                                 '//166.2.126.19/Data/National/Imagery/Aerial_Photography/NAIP/Raw_DOQQs/'], doqq_key = 'DOQQ'):
    Dict = nas_dir_getter(key_list, nas_list)

    out = state_dirs_to_doqq_dirs(Dict, doqq_key)
    print 'dict', Dict
    print 'out', out
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
                    dir_list = [],
                    doqq_key = 'DOQQ',zone = '', res = '', datum = 'nad83',clip_to_extent = True, Buffer = 0, resampling_method = 'cubic',
                    Format = 'HFA', mosaic_only = True, download_images = False, retain_original_projection = True,overwrite = False, negative_buffer = 0):
    if type(extent_raster_or_shapefile) == list:
        coords = extent_raster_or_shapefile
        gdal_coords = str(coords[0]) + ' ' + str(coords[1]) + ' ' + str(coords[2]) + ' ' + str(coords[3])
    else:
        if os.path.splitext(extent_raster_or_shapefile)[1] == '.shp':
            info = shape_info(extent_raster_or_shapefile, False, True)
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
    if dir_list == []:
        print 'Finding quads that intersect image/shapefile', coordinates


        Dirs = get_doqq_dirs(state_list, nas_list = nas_list, doqq_key = doqq_key)
        dir_list = []
        for Dir in Dirs:
            dir_list.append(Dirs[Dir])
    print 'Dir_list', dir_list
    print 'dirs', Dirs

    quads = quad_coords(coordinates)
    print 'quads', quads
    quad_list = quad_getter(quads, dir_list)
    #print 'quads', quad_list

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
def combo_raster(raster1, raster2, raster1_values = [], raster2_values = []):
    r1 = raster(raster1)
    r2 = raster(raster2)

#Dir = 'R:\NAFD\Ancillary\FMask_VCT_Mask_Comparison\Masks/'

def combo_n_list(List, n_list, remove_dups = True):
    out_list = []
    for n in n_list:
        for pm in combinations(List, n):
            out_list.append(pm)
    if remove_dups == True:
        out_list = remove_duplicates(out_list)
    return out_list
#########################################################################
def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [numpy.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = numpy.prod([x.size for x in arrays])
    if out is None:
        out = numpy.zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:,0] = numpy.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out
#########################################################
out = None
rast = None
array = None

