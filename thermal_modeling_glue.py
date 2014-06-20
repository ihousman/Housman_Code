import os, sys, math, random, string, shutil
from dbfpy import dbf
#r_numpy_dir ='E:/Thermal_Mapping/R/Scripts/VB/Tools/'

##if r_numpy_dir not in sys.path:
##    print 'Adding', r_numpy_dir,'to path list'
##    sys.path.append(r_numpy_dir)
from r_numpy_lib import *
from time_series_lib import *
from access_db_lib import *
###############################################################################
cwd = os.getcwd()
parts = cwd.split('\\')
cwd = ''
for part in parts:
    cwd += part + '/'
############################################################################
#root = '//166.2.126.25/rseat/Programs/RSSC/fy2012/Projects/10025_R&D_Thermal_Mapping/02_Data-Archive/02_Inputs/'
root = 'O:/02_Inputs/'
city = 'Bend'
sensor = 'Aster'
datum = 'NAD83'
calibration_field = 'PCT_IMPV'
combo_range = range(2,5)
zone_dict = {'Atlanta': 16, 'Baltimore' : 18, 'Bend' : 10}
res_dict = {'Aster': 90, 'MODIS' : 1000}
point_count_dict = {'Aster': 10000, 'MODIS' : 10000}
point_count = point_count_dict[sensor]
if sensor == 'Aster' and city == 'Bend':
    point_count = 12000
try:
    res = res_dict[sensor]
except:
    res = '90'
try:
    zone = zone_dict[city]
except:
    zone = '16'
############################################################################
base_dir = root + sensor + '/' + city + '/'
inputs_dir = root + sensor + '/' + city + '/Inputs/'
outputs_dir = root + sensor + '/' + city + '/Set_Model_Test_Outputs_RF_Quick_Test2/'
if os.path.exists(outputs_dir) == False:
    os.makedirs(outputs_dir)
calibration_dir = inputs_dir + 'Calibration/'
l_spectral_dir = inputs_dir + 'Landsat_Spectral/'
l_thermal_dir = inputs_dir + 'Landsat_Thermal/'
nlcd_dir = inputs_dir + 'NLCD/'
terrain_dir = inputs_dir + 'Terrain/'
thermal_dir = inputs_dir + 'Thermal/'
thermal_temp_dir = inputs_dir + 'Thermal_Temp/'
time_stack_dir = inputs_dir + 'Time_Stacks/'
m_time_stack_dir = inputs_dir + 'Thermal_Stack/'
thermal_stack_dir = inputs_dir + 'Thermal_Stack_inputs/'
spectral_dir = inputs_dir + 'Spectral/'
mask_dir = inputs_dir + 'Mask/'
anc_master = root + 'Ancillary/Rasters/'
reporting_dir = base_dir + 'Reporting/'

dir_list = [inputs_dir, outputs_dir, calibration_dir, l_spectral_dir, l_thermal_dir, nlcd_dir, terrain_dir,
            nlcd_dir, terrain_dir, thermal_dir, thermal_temp_dir, time_stack_dir,
            m_time_stack_dir, thermal_stack_dir, spectral_dir, mask_dir, reporting_dir]
for Dir in dir_list:
    if os.path.exists(Dir) == False:
        os.makedirs(Dir)
if os.path.exists(reporting_dir) == False:
    os.makedirs(reporting_dir)
############################################################################
try:
    images = filter(lambda i: os.path.splitext(i)[1] == '.img', os.listdir(mask_dir))
    mask_layer = mask_dir + images[0]
    
    info = raster_info(mask_layer)
    coords = info['gdal_coords']
except:
    mask_layer = None
nlcd_lc = anc_master +'nlcd2006_landcover_2-14-11.img'
nlcd_impv = anc_master + 'nlcd2006_impervious_5-4-11.img'

nlcd_impv_clp = nlcd_dir + city + '_' + sensor + '_NLCD_impv.img'
nlcd_lc_clp = nlcd_dir + city + '_' + sensor + '_NLCD_lc.img'


sample_city_dict = {'Atlanta': 'Atlanta', 'Baltimore': 'balt', 'Bend' : 'Bend'}
try:
    pi_calibration = calibration_dir + sample_city_dict[city] + '_sample.shp'
except:
    pi_calibration = calibration_dir + 'anywhere_sample.shp'
nlcd_calibration = calibration_dir + 'nlcd_sample.shp'
nlcd_calibration_a = calibration_dir + 'nlcd_sample_a.shp'
nlcd_calibration_w = calibration_dir + 'nlcd_sample_w.shp'
pi_nlcd_calibration = calibration_dir + 'pi_nlcd_sample.shp'


############################################################################
def modis_mosaicker(Dir = thermal_temp_dir, pair_key_list = ['A2006009', 'A2006057', 'A2006233'], band_extensions = ['_1_t.tif', '_5_t.tif'],extension = '.tif'):
    Files = filter(lambda i: os.path.splitext(i)[1] == extension, os.listdir(Dir))
    Files = map(lambda i: Dir + i, Files)
    day_night_dict = {'1' : 'day', '5': 'night'}
    print Files
    image_pairs = []
    for key in pair_key_list:
        for band in band_extensions:
            temp = [key, band]
            for File in Files:
                if File.find(key) > -1 and File.find(band) > -1:
                    temp.append(File)
                    print os.path.basename(File), key, band
            image_pairs.append(temp)
    for pair in image_pairs:
        if int(pair[0][-3:]) > 190:
            season = 'summer'
        else:
            season = 'winter'
        output = Dir + pair[0] + os.path.splitext(pair[1])[0] + '_' + season + '_' + day_night_dict[pair[1][1]] + extension
        print output
        if os.path.exists(output) == False:
            mosaic(pair[2:], output, res = 1000, zone = zone, Format = 'GTiff',datum = datum,resampling_method = 'cubic')
                
############################################################################

def list_to_pairs(image_list, key_list):
    temp_list = []
    for key in key_list:
        temp = []
        for image in image_list:
            if image.find(key) > -1:
                temp.append(image)
        temp_list.append(temp)
    return cbind(temp_list)
def tile_set(image_list, key = '.split(".")[2]'):
    tile_list = []
    for image in image_list:
        exec('tile_list.append(image' + key + ')')
    return list(set(tile_list))

def new_modis_mosaicker(image_list, key_list, output_dir = thermal_stack_dir, smooth = False):
    image_pairs = list_to_pairs(image_list, key_list)
    key_insert = ''
    for key in key_list:
        key_insert += key + '_'
    key_insert = key_insert[:-1]
    out_list = []
    for pair in image_pairs:
        output = pair[0].split(key_list[0])[0] + key_insert + os.path.splitext(pair[0].split(key_list[0])[1])[0] + '.img'
        if smooth == True:
            to = os.path.splitext(output)[0] + '_coarse.img'
            to_foc = os.path.splitext(output)[0] + '_coarse_mean.img'
            if os.path.exists(to) == False:
                reproject(pair, to, zone = zone, datum = datum, clip_extent = coords, resampling_method = 'cubic')
            if os.path.exists(to_foc) == False:
                focal_filter(to, to_foc)
            pair = [to_foc]
        if os.path.exists(output) == False:
            reproject(pair, output, zone = zone, datum = datum, res = res, clip_extent = coords, resampling_method = 'cubic')
        out_list.append(output)
    return out_list
i_dir = thermal_dir
o_dir = i_dir
def modis_stacker(i_dir = i_dir, o_dir = o_dir, day_key = '_1_t.tif', night_key = '_5_t.tif', smooth = False):
    day_images = map(lambda i: i_dir + i, filter(lambda i: i.find(day_key)  > -1, os.listdir(i_dir)))
    night_images = map(lambda i: i_dir + i, filter(lambda i: i.find(night_key) > -1, os.listdir(i_dir)))
    day_stack = i_dir + city + '_MODIS_day.img'
    night_stack = i_dir + city + '_MODIS_night.img'
    day_reproject = os.path.splitext(day_stack)[0] + '_proj.img'
    tiles_d = tile_set(day_images)
    tiles_n = tile_set(night_images)
    day_stack_list = new_modis_mosaicker(day_images, tiles_d, smooth = smooth)
    night_stack_list = new_modis_mosaicker(night_images, tiles_n, smooth = smooth)
##    if os.path.exists(day_stack) == False:
##        stack(day_stack_list, day_stack, day_stack_list[0])
##    if os.path.exists(night_stack) == False:
##        stack(night_stack_list, night_stack, night_stack_list[0])
##
##        
    #for pair in image_pairs
    #reproject(day_images, day_stack, zone = zone, datum = datum, res = res, resampling_method = 'cubic')
    #if os.path.exists(day_stack) == False:
        #stack(day_images, day_stack, day_images[0])
    #thermal_prep(Dir = Dir, extension = '.img')
    #reproject(day_stack, day_reproject, zone = zone, datum = datum, res = res, resampling_method = 'cubic')
############################################################################
def shp_to_mask(Dir = mask_dir):
    File = filter(lambda i : os.path.splitext(i)[1] == '.shp', os.listdir(Dir))[0]
    print File
    output = os.path.splitext(File)[0] + '.img'
    shapefile_to_raster(Dir + File, Dir + output, resolution = str(res))
############################################################################
def common_extent_maker(Dir = thermal_dir, extension = '.tif'):
    Files = filter(lambda i: os.path.splitext(i)[1] == extension, os.listdir(Dir))
    Files = map(lambda i: Dir + i, Files)
    print Files
    proj_list = []
    for File in Files:
        output = os.path.splitext(File)[0] + '_proj.img'
        proj_list.append(output)
        if os.path.exists(output) == False:
            reproject(File, output, zone = str(zone), datum = datum, res = res, resampling_method = 'cubic')

    clips = clip_list(proj_list)
    thermal_list = stack_clip(clips, Dir, lt_no = 2001)
    make_mask(thermal_list[0], mask_dir + city + '_' + sensor + '_mask.img')
    for image in proj_list:
        os.remove(image)
        try:
            os.remove(image + '.aux.xml')
        except:
            print image + '.aux.xml', 'does not exist'
    for image in clips:
        os.remove(image)
        try:
            os.remove(image + '.aux.xml')
        except:
            print image + '.aux.xml', 'does not exist'
    for image in thermal_list:
        os.remove(image)
        try:
            os.remove(image + '.aux.xml')
        except:
            print image + '.aux.xml', 'does not exist'
    #shutil.copy(thermal_list[0], mask_dir + os.path.basename(thermal_list[0]))
############################################################################
def thermal_prep(Dir = thermal_dir, extension = '.tif'):
    Files = filter(lambda i: os.path.splitext(i)[1] == extension, os.listdir(Dir))
    Files = map(lambda i: Dir + i, Files)
    info = raster_info(mask_layer)
    coords = info['gdal_coords']
   
    for File in Files:
        out_proj = os.path.splitext(File)[0] + '_proj.img'
        clip_file = os.path.splitext(out_proj)[0] + '_clip.img'
        
        
        if os.path.exists(out_proj) == False:
            reproject(File, out_proj, zone = str(zone), datum = datum, clip_extent = coords, res = res, resampling_method = 'cubic')

    
        if os.path.exists(clip_file) == False:
            mask(out_proj, mask_layer, clip_file)
            
    #clips = clip_list(proj_list)
    #thermal_list = stack_clip(clips, Dir, lt_no = 2001)
    #shutil.copy(thermal_list[0], mask_dir + os.path.basename(thermal_list[0]))
############################################################################
def modis_ts_masker(Dir = time_stack_dir):
    Files = map(lambda i : Dir + i, filter(lambda i: os.path.splitext(i)[1] == '.img' and i.find('_mask.img') == -1, os.listdir(Dir)))
    for File in Files:
        mask_output = os.path.splitext(File)[0] + '_mask.img'
        if os.path.exists(mask_output) == False:
            mask(File, mask_layer, mask_output)
############################################################################
def nlcd_prep(Dir = nlcd_dir):
    print 'yay'
    nlcd_clip(mask_layer, nlcd_lc_clp, nlcd_lc)
    nlcd_clip(mask_layer, nlcd_impv_clp, nlcd_impv, resampling_method = 'cubic', mask_method = 'add')
############################################################################
def terrain_prep(Dir = terrain_dir):
    dem = terrain_dir + city + '_' + sensor + '_DEM.img'
    if os.path.exists(dem) == False:
        dem_clip(mask_layer, dem, datum = datum, res = res, zone = zone, Buffer = 0)
    dem_derivatives(dem, Dir)

############################################################################
#def landsat_thermal_rename(Dir = l_thermal_dir, season_dict = {'Winter': 
############################################################################
def landsat_thermal_prep(Dir = l_thermal_dir, suffix_list = ['_winter.img', '_summer.img','_spring.img', '_fall.img']):
    Files = filter(lambda i: i.find(suffix_list[0]) > -1 or i.find(suffix_list[1]) > -1 or i.find(suffix_list[2]) > -1 or i.find(suffix_list[3]) > -1, os.listdir(Dir))
    Files = map(lambda i: Dir + i, Files)
    info = raster_info(mask_layer)
    coords = info['gdal_coords']
    for File in Files:
        out_proj = os.path.splitext(File)[0] + '_proj.img'
        out_clip = os.path.splitext(out_proj)[0] + '_clip.img'
        if os.path.exists(out_proj) == False:
            reproject(File, out_proj, datum = datum, res = str(res), resampling_method = 'cubic', clip_extent = coords, zone = zone)
        if os.path.exists(out_clip) == False:
            mask(out_proj, mask_layer, out_clip)
############################################################################
def landsat_spectral_prep(Dir = l_spectral_dir, suffix = '.tif'):
    Files = filter(lambda i: i.find(suffix) > -1 , os.listdir(Dir))
    Files = map(lambda i: Dir + i, Files)
    print Files
    info = raster_info(mask_layer)
    coords = info['gdal_coords']
    for File in Files:
        out_proj = os.path.splitext(File)[0] + '_proj.img'
        out_filt = os.path.splitext(File)[0] + '_proj_mean.img'
        out_degrade = os.path.splitext(File)[0] + '_proj_mean_degrade.img'
        out_clip = os.path.splitext(out_proj)[0] + '_clip.img'
        if os.path.exists(out_proj) == False:
            reproject(File, out_proj, datum = datum, res = str(30), resampling_method = 'cubic', clip_extent = coords, zone = zone)
        if os.path.exists(out_filt) == False:
            focal_filter(out_proj, out_filt)
        if os.path.exists(out_degrade) == False:
            reproject(out_filt, out_degrade, datum = datum, res = str(res), resampling_method = 'cubic', clip_extent = coords, zone = zone)
        if os.path.exists(out_clip) == False:
            mask(out_degrade, mask_layer, out_clip)
        unstack(out_clip)
        index_maker(out_clip)
############################################################################
def simple_stack_prep():
    vct_files = map(lambda i: l_thermal_dir + i, filter(lambda i:  i.find('proj_clip.img') > -1 and i.find('VCT') > -1, os.listdir(l_thermal_dir)))
    lpgs_files = map(lambda i: l_thermal_dir + i, filter(lambda i:  i.find('proj_clip.img') > -1 and i.find('LPGS') > -1, os.listdir(l_thermal_dir)))
    ls_files = map(lambda i: l_spectral_dir + i, filter(lambda i:  i.find('proj_clip_4.img') > -1, os.listdir(l_spectral_dir)))
    lpgs_stack = l_thermal_dir + 'Landsat_LPGS_B60_Stack.img'
    vct_stack = l_thermal_dir + 'Landsat_VCT_B60_Stack.img'
    ls_stack = l_spectral_dir + 'Landsat_4_Stack.img'
    if os.path.exists(lpgs_stack) == False:
        stack(lpgs_files, lpgs_stack, lpgs_files[0])
    if os.path.exists(vct_stack) == False:
        stack(vct_files, vct_stack, lpgs_files[0])
    stack(ls_files, ls_stack, ls_files[0])
############################################################################
def stack_prep():
    t_files = map(lambda i: thermal_dir + i, filter(lambda i: i.find('proj_clip.img') > -1, os.listdir(thermal_dir)))
    lt_files = map(lambda i: l_thermal_dir + i, filter(lambda i:  i.find('proj_clip.img') > -1, os.listdir(l_thermal_dir)))
    pair_list = ['summer', 'winter', 'fall', 'day', 'night', 'LPGS', 'VCT']
    stack_dict_t, stack_dict_lt ={}, {}
    
    for pair in pair_list:
        stack_list = []
        for t_file in t_files:
            if t_file.find(pair) > -1:
               
                stack_list.append(t_file)
        stack_dict_t[pair] = stack_list
        stack_list = []
        for lt_file in lt_files:
            if lt_file.find(pair) > -1:
               
                stack_list.append(lt_file)
        stack_dict_lt[pair] = stack_list
        

        for stack_list in stack_dict_lt:
            output_stack = time_stack_dir + 'Landsat_Thermal_' + stack_list + '_time_stack.img'
            
            stack_list = stack_dict_lt[stack_list]
            
            if len(stack_list) > 0 and os.path.exists(output_stack) == False:
                print 'Creating:', output_stack
                stack(stack_list, output_stack, stack_list[0])

        for stack_list in stack_dict_t:
            output_stack = time_stack_dir + 'Aster_Thermal_' + stack_list + '_time_stack.img'
            
            stack_list = stack_dict_t[stack_list]
            
            if len(stack_list) > 0 and os.path.exists(output_stack) == False:
                print 'Creating:', output_stack
                stack(stack_list, output_stack, stack_list[0])
############################################################################
def stack_fit():
    stacks = map(lambda i: time_stack_dir + i, filter(lambda i: i.find('time_stack.img') > -1, os.listdir(time_stack_dir)))
    fun_list = ['numpy.diff']#,'numpy.std','nd_image.gaussian_filter1d', 'stats.zscore', 'stats.linregress']
    args = [['axis = 1'], ['axis = 1'], ['sigma = .2', 'axis = 1', 'order = 3'],['axis = 1'], 'None']
    for stack in stacks:
        t = time_stack(stack)
        fun_no = 0
        for fun in fun_list:
            output = os.path.splitext(stack)[0] + '_' + fun + '.img'
            if os.path.exists(output) == False:
                t.stack_fit(output, fun = fun, args = args[fun_no])

            fun_no += 1
    

        t.rm()
        t = None
    
    
    
############################################################################        
def random_pts(mask_layer = mask_layer, point_count = point_count):
    them_img = os.path.splitext(mask_layer)[0] + '_recode2.img'
    if os.path.exists(them_img) == False:
        make_mask(mask_layer, them_img)
    if os.path.exists(nlcd_calibration) == False:
        stratified_sampler(them_img, [point_count], nlcd_calibration, dt = 'Byte')
    extract_value_to_shapefile(nlcd_calibration, calibration_field, nlcd_impv_clp, 'Real')
############################################################################
modis_breaks = [0,20, 30, 40,50,60,70, 80, 90,101]
def stratified_random_pts(to_strata = nlcd_impv_clp, point_count = point_count, breaks =[0, 70, 101] ,props = [.97, .03]):
    them_img = os.path.splitext(mask_layer)[0] + '_recode2.img'
    if os.path.exists(them_img) == False:
        make_mask(mask_layer, them_img)
    
    r_impv = os.path.splitext(nlcd_lc_clp)[0] + '_recode.img'
##    t_to_strata = os.path.splitext(to_strata)[0] + '_plus1.img'
##    if os.path.exists(t_to_strata) == False:
##        increment_by_mask(to_strata, them_img, t_to_strata)
    #if os.path.exists(r_impv) == False:
    recode(to_strata, r_impv, breaks)
        #except:
            #print 'Could not produce', r_impv
            
    pc_list = []
    points_left = point_count
    for prop in props[:-1]:
        print prop, point_count
        t = int(math.floor(prop * point_count))
        points_left = points_left - t
        pc_list.append(t)
        
    pc_list.append(points_left)
    print pc_list
##    counts = hist([r_impv])[0][1:]
##    tot = sum(counts)
##    prop = [float(x) / float(tot) for x in counts]
##    pc_list = [math.floor(float(x) * float(point_count)) for x in prop]
##    print pc_list
##    print prop
##    print counts
    
    if os.path.exists(nlcd_calibration) == False:
        stratified_sampler(r_impv, pc_list, nlcd_calibration, dt = 'Byte')
    extract_value_to_shapefile(nlcd_calibration, calibration_field, nlcd_impv_clp, 'Real')
############################################################################
def update_pi_field():
    values_txt =calibration_dir + 'Values.txt'
    vo = open(values_txt, 'r')
    lines = vo.readlines()
    vo.close()
    vlist = []
    for line in lines:
        line = float(line[:-1])
        vlist.append(line)
    
    update_field(pi_calibration, calibration_field, vlist)
############################################################################
def pi_nlcd_extract():
    print 'yay'
    if os.path.exists(pi_nlcd_calibration) == False:
        print 'Copying', pi_calibration
        copy_shapefile(pi_calibration, pi_nlcd_calibration)
    extract_value_to_shapefile(pi_nlcd_calibration, calibration_field, nlcd_impv_clp, 'Real')
############################################################################
def image_combo_maker():
    l_t_extensions = ['VCT_summer_proj_clip.img','VCT_winter_proj_clip.img','LPGS_summer_proj_clip.img','LPGS_winter_proj_clip.img']
    l_s_extensions = ['_winter_proj_clip_', '_summer_proj_clip_']
    terr_extension = sensor +'_DEM'
    therm_extension = '_proj_clip.img'
    if sensor == 'Aster':
        stack_extension = 'numpy.diff.img'
    else:
        stack_extension = '_mask.img'
    l_t_list = []
    l_s_list = []

    if city != 'Bend':
        calibration_shps = [pi_nlcd_calibration, pi_calibration, nlcd_calibration]
    else:
        calibration_shps = [nlcd_calibration]

    for extension in l_t_extensions:
        t_list = []
        for image in os.listdir(l_thermal_dir):
            if image.find(extension) > -1:
                t_list.append(l_thermal_dir + image)
                l_t_list.append(l_thermal_dir + image)

    for extension in l_s_extensions:
        t_list = []
        for image in os.listdir(l_spectral_dir):
            if image.find(extension) > -1:
                t_list.append(l_spectral_dir + image)
                l_s_list.append(l_spectral_dir + image)

    
    terrain = filter(lambda i: i.find(terr_extension) > -1 and i.find('.aux.xml') == -1, os.listdir(terrain_dir))
    terrain = map(lambda i : terrain_dir + i, terrain)


    thermal = filter(lambda i: i.find(therm_extension) > -1, os.listdir(thermal_dir))
    thermal = map(lambda i : thermal_dir + i, thermal)

    t_stack =  filter(lambda i: i.find(stack_extension) > -1, os.listdir(time_stack_dir))
    t_stack = map(lambda i : time_stack_dir + i, t_stack)
    
    lists = [thermal, l_t_list]#, t_stack]#, terrain, l_s_list]
    #lists.append(['terrain'])
    #lists.append(['l_s_list'])
    big_list = []
    for List in lists:
        for path in List:
            big_list.append(path)
    big_list.append(terrain)
    big_list.append(t_stack)
  
    if len(l_s_list) > 0:
        big_list.append(l_s_list)
    combos = combo_n_list(big_list, combo_range)
    out_list = []
    for combo in combos:
        temp = []
        for image in combo:
            if type(image) == list:
                for piece in image:
                    temp.append(piece)
            else:
                temp.append(image)
        out_list.append(temp)
    return calibration_shps, out_list
############################################################################
def image_set_maker():
    l_t_extensions = ['VCT_summer_proj_clip.img','VCT_winter_proj_clip.img', 'VCT_spring_proj_clip.img', 'VCT_fall_proj_clip.img',
                      'LPGS_summer_proj_clip.img','LPGS_winter_proj_clip.img', 'LPGS_spring_proj_clip.img','LPGS_fall_proj_clip.img']
    #l_s_extensions = ['_winter_proj_clip_', '_summer_proj_clip_', '_spring_proj_clip_', '_fall_proj_clip_']
    l_s_extensions = ['_proj_clip_5.img', '_proj_clip_1.img']
    m_s_extensions = ['_2_t.img', '_1_t.img']
    
    terr_extension = sensor +'_DEM'
    if sensor == 'MODIS' and city == 'Bend':
        therm_extension = '_proj_clip.img'
    elif sensor == 'MODIS':
        therm_extension = '_t.img'
    else:
        therm_extension = '_proj_clip.img'
        
    if sensor == 'Aster' and city != 'Bend':
        stack_extension = 'numpy.diff.img'
    elif sensor == 'Aster' and city == 'Bend':
        stack_extension = '.img'
    else:
        stack_extension = '_mask.img'
    l_t_list = []
    l_s_list = []
    

    if city != 'Bend':
        calibration_shps = [pi_nlcd_calibration, pi_calibration, nlcd_calibration]
    elif sensor == 'MODIS':
        calibration_shps = [nlcd_calibration, nlcd_calibration_a, nlcd_calibration_w]
    else:
        calibration_shps = [nlcd_calibration]
   
    if sensor == 'MODIS':
        m_s_list = []
        for extension in m_s_extensions:
            
            for image in os.listdir(spectral_dir):
                if image.find(extension) > -1:
                    m_s_list.append(spectral_dir + image)
     
    for extension in l_t_extensions:
        t_list = []
        for image in os.listdir(l_thermal_dir):
            if image.find(extension) > -1:
                t_list.append(l_thermal_dir + image)
                l_t_list.append(l_thermal_dir + image)

    for extension in l_s_extensions:
        t_list = []
        for image in os.listdir(l_spectral_dir):
            if image.find(extension) > -1:
                t_list.append(l_spectral_dir + image)
                l_s_list.append(l_spectral_dir + image)

    
    terrain = filter(lambda i: i.find(terr_extension) > -1 and i.find('.aux.xml') == -1, os.listdir(terrain_dir))
    terrain = map(lambda i : terrain_dir + i, terrain)


    thermal = filter(lambda i: i.find(therm_extension) > -1, os.listdir(thermal_dir))
    thermal = map(lambda i : thermal_dir + i, thermal)

    t_stack =  filter(lambda i: i.find(stack_extension) > -1, os.listdir(time_stack_dir))
    t_stack = map(lambda i : time_stack_dir + i, t_stack)
    
    lists = [thermal, l_t_list, terrain, t_stack, l_s_list]#, t_stack]#, terrain, l_s_list]
    if sensor == 'MODIS':
        lists.append(m_s_list)
    #lists.append(['terrain'])
    #lists.append(['l_s_list'])
    big_list = []
    for List in lists:
        if len(List) > 0:
            big_list.append(List)
    
    
##    combos = combo_n_list(big_list, combo_range)
##    out_list = []
##    for combo in combos:
##        temp = []
##        for image in combo:
##            if type(image) == list:
##                for piece in image:
##                    temp.append(piece)
##            else:
##                temp.append(image)
##        out_list.append(temp)
    return calibration_shps, big_list
#############################################################
def clean_dirs(base_dir, find_key = 'toa'):
    Dirs = os.listdir(base_dir)
    for Dir in Dirs:
        if Dir.find(find_key) > -1:
            try:
                print 'Removing', Dir
                
                shutil.rmtree(base_dir + Dir, ignore_errors = True)
            except:
                print 'Could not remove', Dir
############################################################################
#print image_combo_maker()
def run_models(lists):
    pop_list = ['AST_08', 'Baltimore_Aster_','_proj', '_clip', '_intersection']
    key_list = ['MOD11A2', 'MYD09Q1', 'MYD11A2', 'AST', 'win', 'sum', 'day','night', 'DEM', 'VCT_summer', 'LPGS_s', 'VCT_w', 'LPGS_w', 'toa_s', 'toa_w', 'diff', 'linregress']
    samples = lists[0]
    combos = lists[1]
    
    for sample in samples:
        print sample
        counter = 5
        
        for combo in combos[4:]:
            
            if counter%2 != 0 or counter%2 == 0:
                out_dir =outputs_dir + str(counter) + '_' + os.path.basename(os.path.splitext(sample)[0]) 
                combo_piece = ''
                for piece in combo:
                    for key in key_list:
                        if piece.find(key) > -1 and out_dir.find(key) == -1:
                            out_dir += '__' +key
                
                if os.path.exists(out_dir) == False:
                    os.makedirs(out_dir)

                out_dir += '/'
                predictor_list = []
                training_points = out_dir + os.path.basename(sample)
                if os.path.exists(training_points) == False:
                    copy_shapefile(sample, training_points)
               
                for raster in combo:
                    local_rast = out_dir + os.path.basename(raster)
                    predictor_list.append(local_rast)
                    if os.path.exists(local_rast) == False:
                        shutil.copy(raster, local_rast)
                
                cubist_output = out_dir.split('/')[-2] + '_cubist_output.img'
                rf_output = out_dir.split('/')[-2] + '_rf_output.img'
                svm_output = out_dir.split('/')[-2] + '_svm_output.img'
                caret_output = out_dir.split('/')[-2] + '_caret_output.img'
                boot_cv_output = out_dir.split('/')[-2] + '_boot_cv_output.img'
                
                which = ['rf']

                if 'cubist' in which:
                    if os.path.exists(out_dir + cubist_output) == False:
                        print 'Producing:', cubist_output
                        raster_cubist(out_dir, training_points, calibration_field, predictor_list, cubist_output, 5)
                        
                if 'rf' in which:
                    if os.path.exists(out_dir + rf_output) == False:
                        print 'Producing:', rf_output
                        raster_rf(out_dir, training_points, calibration_field, predictor_list, rf_output)

                if 'svm' in which:
                    if os.path.exists(out_dir + svm_output) == False:
                        print 'Producing:', svm_output
                        raster_svm(out_dir, training_points, calibration_field, predictor_list, svm_output)

                if 'caret' in which:
                    if os.path.exists(out_dir + caret_output) == False:
                        print 'Producing:', caret_output
                        raster_caret(out_dir, training_points, calibration_field, predictor_list, caret_output)

                if 'boot_cv' in which:
                    if os.path.exists(out_dir + boot_cv_output) == False:
                        print 'Producing:', boot_cv_output
                        raster_boot_cv(out_dir, training_points, calibration_field, predictor_list, boot_cv_output, model_list = 'c("svm","rf","cubist")',method_list  = 'c("cv", "boot")', count_list = 'c(10, 15)')

               
               
            counter += 1

#############################################################################################################
def variable_counter(variable_list = image_set_maker()[1]):
    tlist = []
    for variable in variable_list:
        for var in variable:
            tlist.append(var)
    variables = unique(tlist)
    out_lines = 'Variable_Name\tUsage_Count\n'
    for variable in variables:
       
        out_lines += os.path.basename(variable) + '\t'
        counter = 0
        for v in tlist:
            if v == variable:
                counter += 1
        
        out_lines += str(counter) + '\n'
        
    var_list_filename = reporting_dir  + city + '_' + sensor + '_variable_count_list_set.txt'
    var_filename_open = open(var_list_filename, 'w')
    var_filename_open.writelines(out_lines)
    var_filename_open.close()
#############################################################################################################
def quick_compare(wd = 'O:/04_Outputs2/',sensor_list = ['Aster','MODIS'],city_list = ['Bend'], base = 'O:/02_Inputs/', o_dir = 'Set_Model_Test_Outputs_RF_Quick_Test2',rscript = cwd + 'rRsac_Tools.r'):
    name_dict = {'linregress': 'Stack_Fit', 'MYD11A2' : 'MODIS_Thermal', 'MOD11A2': 'MODIS_Thermal', 'DEM': 'Topographic', 'MYD09Q1': 'MODIS_Spectral', 'sample_w__' : 'Moist', 'sample_a_' : 'Arid',  'AST':'Aster', 'VCT' : 'Landsat_Thermal', '_diff_': 'Difference', '_toa_': 'Landsat_Spectral',
                '_cubist_': 'Cubist', '_svm_': 'SVM', '_rf_': 'RF'
                 }
    if os.path.exists(wd) == False:
        os.makedirs(wd)
    #city_list = [sys.argv[1]]
    print 'the cities are', city_list
    for sensor in sensor_list:
        for city in city_list:
            sensor_city_dir =  base + sensor + '/' + city + '/'
            nlcd_dir = sensor_city_dir + 'Inputs/NLCD/'
            mask_dir = sensor_city_dir + 'Inputs/Mask/'
            proc_dir = sensor_city_dir + o_dir + '/'
            if os.path.exists(proc_dir) ==  True:
                
                observed = map(lambda i : nlcd_dir + i, filter(lambda i:  i.find('_impv.img') > -1 and os.path.splitext(i)[1] == '.img', os.listdir(nlcd_dir)))[0]

                mask = map(lambda i : mask_dir + i, filter(lambda i:  i.find('_recode2.img') > -1 and os.path.splitext(i)[1] == '.img', os.listdir(mask_dir)))[0]
                
                dirs = map(lambda i: proc_dir + i + '/', filter(lambda i : i.find('nlcd_sample') > -1 and i.find('pi_nlcd') == -1, os.listdir(proc_dir)))
            
                for Dir in dirs:
                    images = map(lambda i: Dir + i, filter(lambda i: os.path.splitext(i)[1] == '.img' and i.find('_sample') > -1  and i[0:4] == 'boot' and i[:2] != 'cv', os.listdir(Dir)))
                    for image in images:
                        
                        out_base_name =  city + '_' 
                        for name in name_dict:
                            if os.path.basename(image).find(name) > -1:
                                out_base_name += name_dict[name] + '_'
                        out_base_name = out_base_name[:-1]
                        if os.path.exists(wd + out_base_name + '_compare_summary.txt') == False:
                            print out_base_name#, os.path.basename(image)
                            
                            call = 'compare("'+wd +'", ref_image = "' + observed + '", predicted_image = "' + image + '", mask = "' + mask + '", out_base_name = "' + out_base_name +'")'
                            r1 = R()
                            #r1.r('print("hello")')
                            #r1.r('library(raster)')
                            #r1.r('raster("' + image + '")')
                            r1.Rfun(rscript, call,save_image = False, restore_image = False)
def compare_compile(wd = 'O:/04_Outputs/'):
    files = map(lambda i: wd + i, filter(lambda i: os.path.splitext(i)[1] == '.txt' and i != 'big_summary.txt', os.listdir(wd)))
    out_lines = []
    for File in files:
        lo = open(File, 'r')
        lines = lo.readlines()
        lo.close()
        lines[1] = os.path.basename(File) + '\t' + lines[1][2:]
        if len(out_lines) == 0:
            out_lines.append(lines[0])
        out_lines.append(lines[1])
    out_file = wd +'big_summary.txt'
    out_o = open(out_file, 'w')
    out_o.writelines(out_lines)
    out_o.close()
#############################################################################################################
#shp_to_mask()     
#modis_mosaicker()
#modis_stacker(smooth = False) #Use for modis prep- change input for spectral or thermal
#common_extent_maker()
#thermal_prep()
#modis_ts_masker()
#nlcd_prep()
#terrain_prep()
#landsat_thermal_prep()
#landsat_spectral_prep()
#simple_stack_prep()
#stack_prep()
#stack_fit()
#random_pts()
#stratified_random_pts()
#pi_nlcd_extract()

#update_pi_field()

#clean_dirs(outputs_dir)

run_models(image_set_maker())
#variable_counter()
#quick_compare()
#compare_compile()
