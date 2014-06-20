from r_numpy_lib import *



def untarball():
    for tar in tarballs:
        untar(tar, not_now)
        #shutil.move(tar, not_now + os.path.basename(tar))
def stack_tif():
    last_piece = os.path.basename(tifs[0]).split('_B')[0]
    stack_list = []
    it_list = []
    for tif in tifs:
        piece = os.path.basename(tif).split('_B')[0]
        #print piece
        if piece != last_piece:
            #print tif
            last_piece = piece
            stack_list.append(it_list)
            it_list = []
        it_list.append(tif)
    if len(it_list) > 0:
        stack_list.append(it_list)
    for s in stack_list:
        print s
        output = Dir + os.path.basename(s[0]).split('_B1')[0] + '.tif'
        if os.path.exists(output) == False:
            stack(s, output, df = 'GTiff')
        else:
            print 'Already created', output


        
def clip_imagery(sat, images):
    out_list = []
    coords = shape_info(sat)['gdal_coords']
    for image in images:
        it = raster_info(image)
        ct = it['coords']
        
        output = ci_dir + os.path.basename(os.path.splitext(image)[0]) + '_clip.tif'

        if os.path.exists(output) == False:
            reproject(image, output, clip_extent = coords, resampling_method = 'cubic')
        out_list.append(output)
    return out_list

def indice_maker(clips):
    for clip in clips:
        index_maker(clip, band_dict = {'blue': 1, 'green' : 2, 'red' : 3, 'nir' : 4, 'swir1' : 5, 'swir2' : 7})
######################################################################
base_dir = 'C:/Users/ihousman/Documents/Zambia/Analysis/'
Dir = base_dir + 'Imagery/'
keep_dir = Dir + 'Keep/'
sa_dir = base_dir + 'SA/'
ci_dir = base_dir + 'CI_Sorted/'
not_now = Dir + 'Not_Now/'
if os.path.exists(not_now) == False:
    os.makedirs(not_now)
    
tarballs =glob(not_now, '.gz')
tifs = glob(not_now, '.TIF')
sa = sa_dir + 'LTSS_SA_N.shp'
sa_nw = sa_dir + 'map_extents_NW_N.shp'
whole_images = glob(keep_dir, '.tif')             
if os.path.exists(ci_dir) == False:
    os.makedirs(ci_dir)
######################################################################

#untarball()
#stack_tif()
clips = clip_imagery(sa_nw, whole_images)
indice_maker(clips)
index_name = 'nbr'
indices = glob_find(ci_dir, '_clip_' + index_name)
nbr_stack = ci_dir + index_name + '_stack_select.img'
stack(indices, nbr_stack)



