#Written by: Ian Housman
#Remote Sensing Applications Center USDA FS
#Contact: ihousman@fs.fed.us
##################################################
#Import necessary modules
from r_numpy_lib import *
from erdas_model_maker import *
temp_dir = cwd + 'temp/'
if os.path.exists(temp_dir) == False:
    os.makedirs(temp_dir)
##############################################################################################################################################################################################################
#If the images are not part of the typical image server file structure, this will create a lookup table
#The pseudo_image_server is just a table with the image name, coordinates, and proj4 projection info
#The object can return a list of images that a given shapefile intersects as well 
class pseudo_image_server:
    def __init__(self, folder_or_list, extension_list = ['.tif'], lookup_table = ''):
        folder = folder_or_list
        if lookup_table == '':
            if folder[-1] == '/':
                ft = folder[:-1]
            else:
                ft = folder
            self.lookup_table = temp_dir + ft.split('/')[-1] + '_lookup_table.txt'
            print self.lookup_table
            #raw_input()
        else:
            self.lookup_table = lookup_table
        self.image_list = []
        #If there is no lookup, one will be created
        #Creating a lookup table allows for faster image lookup than setting up one each time
        if os.path.exists(self.lookup_table) == False:
            out_table = 'Image\tCoords\tProj4\n'
            images = map(lambda i : folder + i, filter(lambda i: os.path.splitext(i)[1] in extension_list, os.listdir(folder)))
            for image in images:
                print image
                info = raster_info(image)
                coords, proj4 = info['coords'], info['proj4']
                out_table += image + '\t' + str(coords) + '\t' + str(proj4)+ '\n'
            ot = open(self.lookup_table, 'w')
            ot.writelines(out_table)
            ot.close()
       
        lo = open(self.lookup_table, 'r')
        lo_lines = lo.readlines()
        self.lookup_dict = []
        for line in lo_lines[1:]:
            line = line.split('\t')
            line[-1] = line[-1][:-1]
            self.lookup_dict.append(line)
        print 'Finished settup up lookup table'
    #Find any image that intersects the shapefile and append them to a list
    def get_images(self, shapefile):
        info = shape_info(shapefile)
        coords = info['coords']
        proj4 = info['proj4']
       
        if self.lookup_dict[0][2] != proj4:
                warning = showwarning('Different Projections', 'Image projection: ' + self.lookup_dict[0][2] + '\nStudy area projection: ' + proj4)
        
        for image in self.lookup_dict:
            image_coords = eval(image[1])
            if intersects(coords, image_coords) == True: self.image_list.append(image[0])
        return self.image_list
##############################################################################################################################################################################################################    
def intersection_offset(sa_coords, image_coords, res):
    difference =  numpy.subtract(sa_coords, image_coords)
    adjusted_diff = difference/res
    xstart = (sa_coords[0] - image_coords[0])/res
    if xstart < 0:
        xstart = 0
    ystart = (sa_coords[1] - image_coords[1])/res
    print ystart, sa_coords[1], image_coords[1]
##    print adjusted_diff
##    adjusted_diff[0] = math.floor(adjusted_diff[0])
##    adjusted_diff[1] = math.ceil(adjusted_diff[1])
##    adjusted_diff[2] = math.floor(adjusted_diff[2])
##    adjusted_diff[3] = math.ceil(adjusted_diff[3])
##    if adjusted_diff[0] < 0:
##        adjusted_diff[0] = 0
##    if adjusted_diff[1] < 0:
##        adjusted_diff[1] = 0
##    if adjusted_diff[2] > 0:
##        adjusted_diff[2] = -1
##    if adjusted_diff[3] < 0:
##        adjusted_diff[3] = -1
##    print adjusted_diff
##    return adjusted_diff
##############################################################################################################################################################################################################
#Object for dealing with a large image list for mosaicking
#Manages path names between degraded and native image names
#Will clip to a study area extent if provided
class large_mosaic:
    def __init__(self, image_list, study_area = ''):
        self.image_list = image_list
        if study_area != '':
            self.study_area = shape_info(study_area)['coords']
        else:
            self.study_area = []
        self.degrade_list = self.image_list
    #Function that will degrade images within the self.image_list list
    def degrade_images(self, res = 10):
        self.degrade_list = []
        for image in self.image_list:
            output = temp_dir + os.path.basename(os.path.splitext(image)[0]) + '_degrade3_' + str(res) + os.path.splitext(image)[1]
            if os.path.exists(output) == False:
                #Gather some information about the rasters
                info = raster_info(image)
                res_o = info['res']
                coords = info['coords']
                
                #offset = intersection_offset(self.study_area, coords, res_o)
                #print offset
                #offset_string = str(int(offset[0])) + ' ' + str(int(offset[1])) + ' ' + str(int(offset[2])) + ' ' + str(int(offset[3]))

                #Set up degrade string for ERDAS bcf command
                offset_string = '0 0 -1 -1'
                res_n = int(math.floor(res/res_o))
                
                call = 'degrade ' + image + ' ' + output + ' ' + offset_string +' -meter -s '+ str(res_n) + ' '+ str(res_n) + ' -e 0'

                
                
                #If the output does not already exist, creates and calls on ERDAS .bcf file
                print 'Degrading:', os.path.basename(image)
                print call
                bcf_name = temp_dir + os.path.splitext(os.path.basename(output))[0] + '.bcf'
                erdas_bcf_maker(call, bcf_name, output, run =True)

            #Checks to make sure the output was created and updates the self.degrade_list list
            if os.path.exists(output) == True:
                self.degrade_list.append(output)

        #Resets teh self.image_list list to the self.degrade_list variable
        self.image_list = self.degrade_list

    def chunk_mosaic(self, output, resampling_method = 'CUBIC CONVOLUTION', clip_extent = [], res = '', integer_or_float = 'Integer', datatype = '', gt_val = 0, run= True, no_quads = 64/4):
        lon_list = []
        lat_list = []
        lat_lon_list = []
        quad_no_list = []
        for image in self.image_list:
                base = os.path.basename(image)
                pieces = base.split('_')
                lat = pieces[1][:2]
                lon = pieces[1][-4:-2]
                quad_no = pieces[1][-2:]
                lat_lon = pieces[1][-2:]
                if lon not in lon_list:
                    lon_list.append(lon)
                if lat not in lat_list:
                    lat_list.append(lat)
                if lat_lon not in lat_lon_list:
                    lat_lon_list.append(lat_lon)
        print lat_lon_list
        #print lon_list
        #print lat_list
        chunk_name_list = []
        for lat_lon in lat_lon_list:
            ct_list = []
            chunk_name = os.path.splitext(output)[0] + '_chunk_' + lat_lon + '.tif'
            chunk_name_list.append(chunk_name)
            print chunk_name
            for image in self.image_list:
                if os.path.basename(image).split('_')[1] == lat_lon:
                    ct_list.append(image)
            erdas_mosaicker(ct_list, chunk_name, resampling_method = resampling_method, integer_or_float = integer_or_float, datatype = datatype, gt_val = gt_val, run = run)
        self.image_list = chunk_name_list

    def generic_chunk_mosaic(self, output, resampling_method = 'CUBIC CONVOLUTION', clip_extent = [], res = '', integer_or_float = 'Integer', datatype = '', gt_val = 0, run= True):
        total_extent = [10000000,10000000,0,0]
        for image in self.image_list[:10]:
            it = raster_info(image)
            ct = it['coords']
            if ct[0] < total_extent[0]:
                total_extent[0] = ct[0]
            if ct[1] < total_extent[1]:
                total_extent[1] = ct[1]
            if ct[2] > total_extent[2]:
                total_extent[2] = ct[2]
            if ct[3] > total_extent[3]:
                total_extent[3] = ct[3]
        itt = self.image_list[:10]
        print sorted(itt)
    #Performs actual mosaic
    def mosaic_list(self, output, resampling_method = 'CUBIC CONVOLUTION', clip_extent = [], res = '', integer_or_float = 'Integer', datatype = '', gt_val = 0, chunk = True, run =False):
        if clip_extent == [] and self.study_area != None:
            clip_extent = self.study_area
       
        if chunk == True:
            #self.chunk_mosaic(output, resampling_method = resampling_method, clip_extent = clip_extent, integer_or_float = integer_or_float, datatype = datatype, gt_val = gt_val, run = run)
            print 'chunking'
            self.generic_chunk_mosaic(output, resampling_method = resampling_method, clip_extent = clip_extent, integer_or_float = integer_or_float, datatype = datatype, gt_val = gt_val, run = run)
        #Uses the erdas_mosaicker function with the list to create the output
        erdas_mosaicker(self.image_list, output, resampling_method = resampling_method, clip_extent = clip_extent, integer_or_float = integer_or_float, datatype = datatype, gt_val = gt_val, run = run)



##############################################################################################################################################################################################################
#folder = '//166.2.126.22/Data/National/Imagery/Aerial_Photography/Resource_Photos/Resource_2006_half_meter_Fishlake/'
##
#naip_dir = '//166.2.126.71/Data_NAIP/National/Imagery/Aerial_Photography/2011_DOQQ/Utah_2011_NAIP_doqqs/Utah_Statewide_DOQQ_2011/'
##
##wd = 'O:/03_Process/fiddle6/'
#study_area = '//166.2.126.25/R4_VegMaps/Dixie_Fishlake/Data/Boundaries_TEMP/Admn_Bndry_Dixie_Buff_1mi.shp'
##
###p = pseudo_image_server(folder)
###quads = p.get_images(study_area)
###print quads
#quads = quad_downloader(study_area, temp_dir, state_list = [], mosaic_only = False, download_images = False, dir_list = [naip_dir])[0]

#l = large_mosaic(quads, study_area = study_area)
#l.degrade_images()
#l.mosaic_list(output = temp_dir + 'test2.img', run =False)
