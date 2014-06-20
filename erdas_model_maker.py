#Partially written by: Ian Housman
#Remote Sensing Applications Center USDA FS
#Contact: ihousman@fs.fed.us
#Uses code also written by: Bonnie Ruefenacht
##################################################
import shutil, os, subprocess, sys, getpass
################################################################################################
erdas_gdal_model_datatype_dict = { 'Byte': '8 BIT UNSIGNED INTEGER', 'Uint16': '16 BIT UNSIGNED INTEGER', 'Int16': '16 BIT SIGNED INTEGER', 'Uint32': '32 BIT UNSIGNED INTEGER', 'Int32': '32 BIT SIGNED INTEGER', 'Float32': 'FLOAT SINGLE', 'Float64': 'FLOAT DOUBLE'}
erdas_datatype_list = []
for dt in erdas_gdal_model_datatype_dict:
    erdas_datatype_list.append(erdas_gdal_model_datatype_dict[dt])
erdas_gdal_bcf_datatype_dict = { 'Byte': 'Unsigned_8_bit', 'uint16': 'Unsigned_16_bit', 'int16': 'Signed_16_bit', 'uint32': 'Unsigned_32_bit', 'int32': 'Signed_32_bit', 'Float32': 'Float_Single', 'Float64': 'FLOAT_DOUBLE'}
integer_or_float_dict = {'Byte' : 'Integer', 'Uint16': 'Integer', 'Int16': 'Integer', 'uint32': 'Integer', 'int32': 'Integer', 'Float32' : 'Float', 'Float64' : 'Float'}
################################################################################################
#Script will try to automatically pull in your username.  If it fails, it will ask for it
try:
    base_username = getpass.getuser()
    capitalized_username = base_username.upper()
except:
    base_username = raw_input('Please enter your username')
    capitalized_username = base_username.upper()
################################################################################################
#The following lines are needed to access ERDAS through Python
USERNAME = base_username
TEMP_DIRECTORY = 'C:/DOCUME~1/' + capitalized_username + '/LOCALS~1/Temp'
################################################################################################
program_files_dir_options = ['C:/Program Files (x86)/', 'C:/Program Files/']
erdas_dir_options = ['C:/ERDAS/', 'C:/Program Files/ERDAS/', 'C:/Intergraph/']
user_dir_options = ['C:\\Users\\', 'C:\\Documents and Settings\\']

for option in program_files_dir_options:
    if os.path.exists(option):
        program_files_dir = option
        break
for option in erdas_dir_options:
    if os.path.exists(option):
        erdas_dir = option
        break
for option in user_dir_options:
    if os.path.exists(option):
        user_dir = option
        break
print 'Program files dir:', program_files_dir
print 'Erdas dir:', erdas_dir
print 'User dir:', user_dir

#Checks ERDAS for available ERDAS versions
IMAGINE_HOME_93 = erdas_dir + 'Geospatial Imaging 9.3'
IMAGINE_HOME_10 = erdas_dir + 'ERDAS Desktop 2010'
IMAGINE_HOME_11 = erdas_dir + 'ERDAS Desktop 2011'
IMAGINE_HOME_13 = erdas_dir + 'ERDAS IMAGINE 2013'
ERDAS = 'C:/PROGRA~2/ERDAS/GEOSPA~1.3/BIN/NTX86/'
if os.path.exists(IMAGINE_HOME_13) == True:
    print 'Using ERDAS 13 to run models'
    IMAGINE_HOME =IMAGINE_HOME_13
    imagine_version = '13'
elif os.path.exists(IMAGINE_HOME_11) == True:
    print 'Using ERDAS 11 to run models'
    IMAGINE_HOME =IMAGINE_HOME_11
    imagine_version = '11'
elif os.path.exists(IMAGINE_HOME_10) == True:
    print 'Using ERDAS 10 to run models'
    IMAGINE_HOME =IMAGINE_HOME_10
    imagine_version = '10'
elif os.path.exists(IMAGINE_HOME_93) == True:
    print 'Using ERDAS 9.3 to run models'
    IMAGINE_HOME =IMAGINE_HOME_93
    imagine_version = '93'

##else:
##    print 'Must install ERDAS IMAGINE to run most programs within this toolbar'
##    answer = raw_input('Do you want to proceed without ERDAS? Y = Yes or N = No  ')
##    if str(answer) == 'Y' or str(answer) == 'y':
##        print 'Continuing without ERDAS'
##        print''
##        print''
##        imageine_version = ''
##    elif str(answer) == 'N' or str(answer) == 'n':
##        print 'Exiting program'
##        print''
##        print''
##        sys.exit()
################################################################################################    
def GetBatLines(bls,bcf):
    BatLines = []
    BatLines.append('@echo off\n')
    if imagine_version == '93':
        BatLines.append('echo lockfile > "'+ user_dir + USERNAME + '\\.imagine930\\batch\\batch.lck"\n')
    elif imagine_version == '10':
        BatLines.append('echo lockfile > "'+ user_dir + USERNAME + '\\.imagine1000\\batch\\batch.lck"\n')
    elif imagine_version == '11':
        BatLines.append('echo lockfile > "'+ user_dir+ USERNAME + '\\.imagine1100\\batch\\batch.lck"\n')
    elif imagine_version == '13':
        BatLines.append('echo lockfile > "'+ user_dir+ USERNAME + '\\.imagine1300\\batch\\batch.lck"\n')
    BatLines.append('set USERNAME=' + USERNAME + '\n')
    BatLines.append('set HOME='+ user_dir + USERNAME + '\n')
##    BatLines.append('set ARCH=NTx86\n')
##    BatLines.append('set ARCHM=ntx86\n')
##    BatLines.append('set TEMP=' + TEMP_DIRECTORY.replace('/','\\') + '\n')
##    BatLines.append('set TMP=' + TEMP_DIRECTORY.replace('/','\\') + '\n')
##    BatLines.append('set IMAGINE_HOME=' + IMAGINE_HOME + '\n')
##    BatLines.append('set ARCHOME=' + IMAGINE_HOME + '\\archome\\ntx86\n')
##    BatLines.append('set ERDAS_APPLICATION_FUNCTIONS_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\ApplicationFunctions;' + IMAGINE_HOME + '\\usr\\lib\\ntx86\\ApplicationFunctions\n')
##    BatLines.append('set ERDAS_ARROWSTYLE_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\Arrows;' + IMAGINE_HOME + '\\etc\\Arrows\n')
##    BatLines.append('set ERDAS_BATCH_DIR=C:/Documents and Settings/' + USERNAME + '/.imagine930\n')
##    BatLines.append('set ERDAS_BIN_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930;' + IMAGINE_HOME + '\\bin\\ntx86\n')
##    BatLines.append('set ERDAS_CFG_DATABASES=\n')
##    BatLines.append('set ERDAS_CFG_PATH=C:\\Documents and Settings\\All Users\\Application Data\\ERDAS\\Geospatial Imaging 9.3\\devices\\ntx86;C:\\Documents and Settings\\All Users\\Application Data\\ERDAS\\Geospatial Imaging 9.3\\etc;C:/Documents and Settings/' + USERNAME + '/.imagine930\n')
##    BatLines.append('set ERDAS_COLOR_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\Colors;' + IMAGINE_HOME + '\\etc\\Colors\n')
##    BatLines.append('set ERDAS_DBCONNECT_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\DBConnect;' + IMAGINE_HOME + '\\usr\\lib\\ntx86\\DBConnect\n')
##    BatLines.append('set ERDAS_DEVICES_PATH=' + IMAGINE_HOME + '\\devices\\ntx86;' + IMAGINE_HOME + '\\devices\n')
##    BatLines.append('set ERDAS_DLL_DIR=' + IMAGINE_HOME + '\\usr\\lib\\ntx86\n')
##    BatLines.append('set ERDAS_ESRI_BIN_PATH=' + IMAGINE_HOME + '\\archome\\ntx86\\bin\n')
##    BatLines.append('set ERDAS_ETC_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930;' + IMAGINE_HOME + '\\fixes;' + IMAGINE_HOME + '\\etc\n')
##    BatLines.append('set ERDAS_EXPRO_DIR=' + IMAGINE_HOME + '\\etc\\expro\n')
##    BatLines.append('set ERDAS_EXPRO_EXC_NAME=exprojections\n')
##    BatLines.append('set ERDAS_FILE_FILTERS_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\FileFilters;' + IMAGINE_HOME + '\\usr\\lib\\ntx86\\FileFilters\n')
##    BatLines.append('set ERDAS_FILLSTYLE_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\FillStyles;' + IMAGINE_HOME + '\\fixes;' + IMAGINE_HOME + '\\etc\\FillStyles\n')
##    BatLines.append('set ERDAS_FONT_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\fonts;' + IMAGINE_HOME + '\\etc\\fonts\n')
##    BatLines.append('set ERDAS_FONT_SERVERS_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\FontServers;' + IMAGINE_HOME + '\\usr\\lib\\ntx86\\FontServers\n')
##    BatLines.append('set ERDAS_GEOMETRIC_MODELS_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\GeometricModels;' + IMAGINE_HOME + '\\usr\\lib\\ntx86\\GeometricModels\n')
##    BatLines.append('set ERDAS_GEOMODEL_INTERFACES_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\GeomodelInterfaces;' + IMAGINE_HOME + '\\usr\\lib\\ntx86\\GeomodelInterfaces\n')
##    BatLines.append('set ERDAS_HELP_DIR=' + IMAGINE_HOME + '\\help\n')
##    BatLines.append('set ERDAS_ICON_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930;' + IMAGINE_HOME + '\\fixes;' + IMAGINE_HOME + '\\icons\n')
##    BatLines.append('set ERDAS_INSTALL_PATH=' + IMAGINE_HOME + '\\install\n')
##    BatLines.append('set ERDAS_LIBRARY_PATH=' + IMAGINE_HOME + '\\usr\\lib\\ntx86\n')
##    BatLines.append('set ERDAS_LINESTYLE_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\LineStyles;' + IMAGINE_HOME + '\\fixes;' + IMAGINE_HOME + '\\etc\\LineStyles\n')
##    BatLines.append('set ERDAS_MODEL_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930;' + IMAGINE_HOME + '\\fixes;' + IMAGINE_HOME + '\\etc\\models\n')
##    BatLines.append('set ERDAS_PDF_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930;' + IMAGINE_HOME + '\\fixes;' + IMAGINE_HOME + '\\defaults\\NTx86;' + IMAGINE_HOME + '\\defaults\n')
##    BatLines.append('set ERDAS_PREFERENCES_PATH=' + IMAGINE_HOME + '\\defaults;C:/Documents and Settings/' + USERNAME + '/.imagine930\n')
##    BatLines.append('set ERDAS_PROJECTION_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\projections;' + IMAGINE_HOME + '\\fixes;' + IMAGINE_HOME + '\\etc\\projections\n')
##    BatLines.append('set ERDAS_PROJECTIONS_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930;' + IMAGINE_HOME + '\\fixes;' + IMAGINE_HOME + '\\etc;' + IMAGINE_HOME + '\\bin\\ntx86\n')
##    BatLines.append('set ERDAS_RASTER_FORMATS_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\RasterFormats;' + IMAGINE_HOME + '\\usr\\lib\\ntx86\\RasterFormats\n')
##    BatLines.append('set ERDAS_RESAMPLE_METHODS_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\ResampleMethods;' + IMAGINE_HOME + '\\usr\\lib\\ntx86\\ResampleMethods\n')
##    BatLines.append('set ERDAS_SCRIPT_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930;' + IMAGINE_HOME + '\\fixes;' + IMAGINE_HOME + '\\scripts\\NTx86;' + IMAGINE_HOME + '\\scripts\n')
##    BatLines.append('set ERDAS_STYLE_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930;' + IMAGINE_HOME + '\\etc\n')
##    BatLines.append('set ERDAS_SYMBOL_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\Symbols;' + IMAGINE_HOME + '\\fixes;' + IMAGINE_HOME + '\\etc\\Symbols;C:/Documents and Settings/' + USERNAME + '/.imagine930;' + IMAGINE_HOME + '\\etc\n')
##    BatLines.append('set ERDAS_TEXTSTYLE_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\TextStyles;' + IMAGINE_HOME + '\\fixes;' + IMAGINE_HOME + '\\etc\\TextStyles\n')
##    BatLines.append('set ERDAS_TM_PALLETTE_PATH=' + IMAGINE_HOME + '\\defaults\\NTx86;' + IMAGINE_HOME + '\\defaults\n')
##    BatLines.append('set ERDAS_VECTFILE_LINK_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\erdas_vectfile_link_loc\n')
##    BatLines.append('set ERDAS_VECTOR_FORMATS_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\VectorFormats;' + IMAGINE_HOME + '\\usr\\lib\\ntx86\\VectorFormats\n')
##    BatLines.append('set ERDAS_VIEWER=' + IMAGINE_HOME + '\\bin\\ntx86\\viewer\n')
##    BatLines.append('set ERDAS_VIRTUAL_MODELS_PATH=C:/Documents and Settings/' + USERNAME + '/.imagine930\\VirtualModels;' + IMAGINE_HOME + '\\usr\\lib\\ntx86\\VirtualModels\n')
##    BatLines.append('set TMPATH=' + IMAGINE_HOME + '\\etc\\terramodel\\NTx86\n')
    BatLines.append('set IMAGINE_BATCH_RUN=1\n')
    if imagine_version == '93' or imagine_version == '10':
        BatLines.append('"' + IMAGINE_HOME + '/bin/ntx86/batchprocess.exe" -bcffile "' + bcf + '" -blsfile "' + bls + '" -logfile "' + os.path.splitext(bcf)[0] + '.log"\n')
    elif imagine_version == '11' or imagine_version == '13':
        BatLines.append('"' + IMAGINE_HOME + '/bin/Win32Release/batchprocess.exe" -bcffile "' + bcf + '" -blsfile "' + bls + '" -logfile "' + os.path.splitext(bcf)[0] + '.log"\n')
    if imagine_version == '93':
        BatLines.append('del "'+ user_dir + USERNAME + '\\.imagine930\\batch\\batch.lck"\n')
    elif imagine_version == '10':
        BatLines.append('del "'+ user_dir + USERNAME + '\\.imagine1000\\batch\\batch.lck"\n')
    elif imagine_version == '11':
        BatLines.append('del "'+ user_dir + USERNAME + '\\.imagine1100\\batch\\batch.lck"\n')
    elif imagine_version == '13':
        BatLines.append('del "'+ user_dir + USERNAME + '\\.imagine1300\\batch\\batch.lck"\n')
    return BatLines
################################################################################################
#Erdas Model maker creates .mdl, .bls, .bcf, and .bat necessary to run ERDAS models from Python
def erdas_model_maker(Model, model_filename, output_name = '', message = '', should_delete = False, run = True):
    #The .mdl is created using the list of strings entered above
    ModelFile = open(model_filename,'w')
    ModelFile.writelines(Model)
    ModelFile.close()
    Output = model_filename
    # make BLS -- it's a necessary but empty file
    bls_filename = os.path.splitext(Output)[0] + '.bls'
    bls = open(bls_filename,'w')
    bls.close()

    # make BCF -- lists the command ERDAS requires to actually run the image processing
    bcf_filename = os.path.splitext(Output)[0] + '.bcf'
    bcf = open(bcf_filename,'w')
    bcf.write('modeler ' + model_filename)
    bcf.close()

    # make BAT -- runs BCF outside of ERDAS
    bat_filename = os.path.splitext(Output)[0] + '.bat'
    bat = open(bat_filename,'w')
    Lines = GetBatLines(bls_filename, bcf_filename)
    bat.writelines(Lines)
    bat.close()

    #Calls on the model through the batch file that calls on the .bls that contains the syntax that IMAGINE can understand
    if os.path.exists(output_name) == False or should_delete == True:
        print''
        print''
        print''
        if run == True:
            print message
            call = subprocess.Popen(bat_filename)
            call.wait()
            print''
            print output_name.split('/')[-1], 'has been created'
        print''
        print''
        print''
        print''
    else:
        print''
        print''
        print 'Already created', output_name.split('/')[-1]

################################################################################################
#Call on for simple ERDAS commands that only use a bcf (mask, reproject....)
def erdas_bcf_maker(bcf, bcf_filename, output_name = '', should_delete = False, run = True):
    Output = bcf_filename
    # make BLS -- it's a necessary but empty file
    bls_filename = os.path.splitext(bcf_filename)[0] + '.bls'
    bls = open(bls_filename,'w')
    bls.close()

    # make BCF -- lists the command ERDAS requires to actually run the image processing
    bcf_filename = os.path.splitext(bcf_filename)[0] + '.bcf'
    bcfo = open(bcf_filename,'w')
    bcfo.write(bcf)
    bcfo.close()

    # make BAT -- runs BCF outside of ERDAS
    bat_filename = os.path.splitext(bcf_filename)[0] + '.bat'
    bat = open(bat_filename,'w')
    Lines = GetBatLines(bls_filename, bcf_filename)
    bat.writelines(Lines)
    bat.close()
    
    #Calls on the model through the batch file that calls on the .bls that contains the syntax that IMAGINE can understand
    if os.path.exists(output_name) == False or should_delete == True:
        print''
        print''
        print''
        if run == True:
            call = subprocess.Popen(bat_filename)
            call.wait()
            print''
            print output_name.split('/')[-1], 'has been created'
        print''
        print''
        print''
        print''
    else:
        print''
        print''
        print 'Already created', output_name.split('/')[-1]

################################################################################################
def erdas_mosaicker(image_list, output, template_shapefile = '', resampling_method = 'CUBIC CONVOLUTION', clip_extent = '', res = '', integer_or_float = '', datatype = '', gt_val = 0, run = True):
    if datatype == '':
        try:
            from r_numpy_lib import raster_info
            dt = raster_info(image_list[0])['dt']
            integer_or_float = integer_or_float_dict[dt]
            print integer_or_float
            datatype = erdas_gdal_model_datatype_dict[dt]
            print integer_or_float, datatype
        except:
            print 'Cannot find datatype of input'
    Model = []
    if res != '':
        try:
            res = int(res)
            Model.append('SET CELLSIZE '+ str(res) + ', '+ str(res) + ' METERS;\n')
        except:
            
            Model.append('SET CELLSIZE MIN;\n')
    else:
        Model.append('SET CELLSIZE MIN;\n')
    if clip_extent == '':
        Model.append('SET WINDOW UNION;\n')
    else:
        ulx = clip_extent[0]
        uly = clip_extent[3]
        lrx = clip_extent[2]
        lry = clip_extent[1]
        window_string = str(ulx) + ', ' + str(uly) + ' : ' + str(lrx) + ', ' + str(lry)

        Model.append('SET WINDOW '+window_string+' MAP;\n')
    Model.append('SET AOI NONE;\n')
    if template_shapefile != '':
        Model.append('Integer VECTOR n1_shp COVER AOI NONE POLYGON RENDER TO MEMORY "' + template_shapefile + '";\n')
    print 'Mosaicking:'
    i = 1
    for image in image_list:
        print image
        vname = 'i_' + str(i)
        Model.append(integer_or_float + ' RASTER '+vname+' FILE OLD PUBINPUT '+resampling_method+' AOI NONE "' + image+ '";\n')
        i += 1

    Model.append(integer_or_float + ' RASTER o_1 FILE DELETE_IF_EXISTING PUBOUT IGNORE 0 ATHEMATIC '+datatype+' "' + output +'";\n')
    Model.append('o_1 = CONDITIONAL{\n')
    i = 1
    for image in image_list:
        Model.append('($i_' + str(i) +  ' GT '+str(gt_val)+') $i_' + str(i) + ',\n')
        i += 1
        
    Model[-1] = Model[-1][:-2] + '};\n'
    Model.append('QUIT;\n')

    temp_folder = os.path.dirname(output) + '/temp/'
    if os.path.exists(temp_folder) == False:
        os.makedirs(temp_folder)
    model_name = temp_folder + os.path.basename(os.path.splitext(output)[0]) + '_model.mdl'
    print 'Running mosaic model:', os.path.basename(model_name)
    erdas_model_maker(Model, model_name, output, run = run)

