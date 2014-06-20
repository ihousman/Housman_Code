#Written by: Ian Housman
#Remote Sensing Applications Center USDA FS
#Contact: ihousman@fs.fed.us
##################################################
from r_numpy_lib import *
from erdas_model_maker import *
#####################################################################################################   
def dem_naip_downloader(shapefile, output, dem_or_naip, res = '', zone = '', datum = 'WGS84', Buffer = 1000, state_list = [], no_data = 0):
    
    #Set up format driver with the proper extension
    Formats = format_dict()
    extension = os.path.splitext(output)[1]
    try:
        Format = Formats[extension]
    except:
        Format = 'HFA'
        output = os.path.splitext(output)[0] + '.img'
        
    #Set up temp folder for models
    temp_folder = os.path.dirname(output) + '/temp/'
    if os.path.exists(temp_folder) == False:
        os.makedirs(temp_folder)
    #Get info about shapefile (will work with a raster as well)
    if os.path.splitext(shapefile)[1] == '.shp':
        info = shape_info(shapefile, False)
    else:
        info = raster_info(shapefile)

    #Set pieces of info to variables  
    crs, gdal_coords, gdal_list_coords = info['proj4'], info['gdal_coords'], info['coords']

    #Create a utm version of the shapefile of the specified zone and datum
    #and get the projected and original coordinates (may also be projected)
    proj_shp, sc, pc = utm_maker(shapefile, output, zone, datum)

    #Create list and string version of the projected coords (pc)
    pc_list = pc
    pc = str(pc[0]) + ', ' + str(pc[1]) + ', ' + str(pc[2]) + ', ' + str(pc[3])

    #Find out if DEM or NAIP is wanted
    if dem_or_naip == 'dem' or dem_or_naip == 'DEM':
        #Calls on the dem_clip function
        #This function returns a list of dem tiles the shapefile intersects
        #and the clip extent (projected coordinates)
        images, clip_extent = dem_clip(proj_shp, output, Buffer = Buffer, create_mosaic = False, res = res)

        #Since DEM tiles are geographic, must convert the extent to geographic
        geog_coords = utm_coords_to_geographic(clip_extent, zone)

        #Call on the erdas_mosaicker function to mosaic the geographic tiles
        geog_output = temp_folder + os.path.basename(os.path.splitext(output)[0]) + '_geog' + os.path.splitext(output)[1]
        
        if os.path.exists(geog_output) == False:
            erdas_mosaicker(images, geog_output, clip_extent = geog_coords, integer_or_float = 'FLOAT', datatype = 'FLOAT SINGLE')
        else:
            print geog_output, 'already exists'

        if os.path.exists(output) == False:
            reproject(geog_output, output, crs = crs, resampling_method = 'cubic', res = res, Format = Format)
        
    elif dem_or_naip == 'naip' or dem_or_naip == 'NAIP':
        #Calls the quad_downloader function
        #This function returns a list of quarter quads the shapefile intersects
        #and the clip extent (projected coordinates)
        images, clip_extent = quad_downloader(proj_shp, output, Buffer = Buffer, state_list = state_list, download_images = False, res = res)
        
        #Call on the erdas_mosaicker function to mosaic the geographic tiles
        t_info = raster_info(images[0])
        crs_t = t_info['proj4']
        if crs_t != crs:
            geog_output = temp_folder + os.path.basename(os.path.splitext(output)[0]) + '_naip_orig' + os.path.splitext(output)[1]
        else:
            geog_output = output
        if os.path.exists(geog_output) == False:
            print clip_extent
            erdas_mosaicker(images, geog_output, clip_extent = clip_extent, res = res, resampling_method = 'NEAREST NEIGHBOR')

        if geog_output != output and os.path.exists(output) == False:
            reproject(geog_output, output, crs = crs, resampling_method = 'cubic', Format = Format, res = res)
            
#####################################################################################################
#Set up input and output folders
input_dir = 'O:/03_Process/fiddle5/'
output_dir = 'O:/03_Process/fiddle5_outputs/'
#########################################
#Define extensions for inputs and outputs (can use rasters or shapefiles for outputs)
#Currently only fully supports .tif and .img 
in_extension = '.shp'

naip_out_extension = '_naip.img'
dem_out_extension = '_dem.img'
#########################################
#Set up inputs (leave wild card to batch all shapefiles in folder in a batch)
Input = input_dir + '*'
#########################################
#Choose zone, datum, buffer (meters), and resolution
zone = '14'
datum = 'WGS84'
res_dict = {'naip': 5, 'dem' : 10}
Buffer = 500
########################################
#Choose 'dem' or 'naip' or list both
dem_or_naip = ['dem', 'naip']
########################################
if os.path.exists(output_dir) == False:
    os.makedirs(output_dir)
if Input[-1] == '*':
    inputs = map(lambda i : input_dir + i, filter(lambda i : os.path.splitext(i)[1] == in_extension, os.listdir(input_dir)))
else:
    inputs = [Input]

for Input in inputs:
    zt = shape_info(Input, False)['zone']
    if zt == '':
        zt = zone
    print zt
    for d_o_n in dem_or_naip:
        exec('output = output_dir + os.path.basename(os.path.splitext(Input)[0]) + ' + d_o_n + '_out_extension')
        if os.path.exists(output) == False:
            dem_naip_downloader(Input, output, dem_or_naip = d_o_n, res = res_dict[d_o_n], zone = zt, datum = datum, Buffer = Buffer)




