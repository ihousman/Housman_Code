from r_numpy_lib import *
from erdas_model_maker import *

Dir = '//166.2.126.214/Data/National/Terrain/NED/grid/'
to_dir = 'O:/02_Inputs/Ancillary/Rasters/temp/'
ns_extent=[25, 50]
folders = filter(lambda i: os.path.isdir(Dir + i), os.listdir(Dir))
image_list = []
##for folder in folders:
##    if folder.find('n') > -1 and folder.find('w') > -1:
##        n = int(folder[1:3])
##        w = int(folder[4:])
##        if n >= ns_extent[0] and n <= ns_extent[1]:
##            folder = Dir + folder + '/'
##            dirs = glob_find(folder, 'grdn')[0]
##            if os.path.exists(dirs):
##                image_list.append(dirs)
##i = 0
##
##for image in image_list:
##    out = to_dir + os.path.basename(image) + '_t.tif'
##    if os.path.exists(out) == False and i%2 != 0:
##        convert(image, out)
##
##    i += 1
#erdas_mosaicker(image_list, to_dir + 'big_dem_31_35.img', run = False)

def unchip(in_list, output, dt = ''):
    xmaxs, ymaxs, xmins, ymins = [],[],[],[]
    wl = []
    hl = []
    for image in in_list:
        info = raster_info(image)
        #print info
        coords = info['coords']
        width = info['width']
        height = info['height']
        print info['transform']
        xmaxs.append(coords[2])
        ymaxs.append(coords[-1])
        xmins.append(coords[0])
        ymins.append(coords[1])

        
        wl.append(width)
        hl.append(height)
    
    xmin, ymin, xmax, ymax = min(xmins), min(ymins), max(xmaxs), max(ymaxs)
    res = float(info['res'])
    height = float((ymax- ymin))/float(res)
    width = float((xmax - xmin))/float(res)
    if dt == '':
        dt = info['dt']
    transform = [xmin, res, 0.0, ymax, 0.0, -res]
    print transform
    print height, width
    #ti = tiled_image(output, width = width, height = height, bands = info['bands'], dt =  dt, transform = transform, projection = info['projection'])

##
##    for image in in_list:
##        info = raster_info(image)
##        coordst = info['coords']
##        rest = info['res']
##        xmint = coordst[0]
##        ymaxt = coordst[-1]
##       
##        xoff = round((xmint-xmin)/rest)
##        yoff = round((ymax - ymaxt)/rest)
##        print xmin, ymax, xmint, ymaxt, xoff, yoff, rest
##        print
##        print
        #print os.path.basename(image), xoff, yoff
        #rast = brick(image, dt = dt)
        #ti.add_tile(rast, xoff, yoff)
##tifs = glob_find(to_dir, '_t.tif')
##i = 0
##for tif in tifs:
##    out = os.path.splitext(tif)[0] + '_30m_16b.tif'
##    info = raster_info(tif)
##    res = info['res'] * 3
##
##    if os.path.exists(out) == False and i%2 != 0:
##        reproject(tif, out, res = res, dt = 'Int16')
##    i += 1

##tifs = glob_find(to_dir, '_30m_16b.tif')
##nl = 0
##il = []
##for tif in tifs:
##    tn = os.path.basename(tif)
##    n = int(tn.split('grdn')[1][:2])
##    if nl == n:
##        il.append(tif)
##    else:
##        out = to_dir + str(n-1) + 'n_dem_mosaic.img'
##        print out
##        if os.path.exists(out) == False:
##            erdas_mosaicker(il, out,  run = True)
##        else:
##            print 'Already created', out
##        il = []
##        nl = n
##out = to_dir + str(n) + 'n_dem_mosaic.img'
##if os.path.exists == False:
##    erdas_mosaicker(il, out,  run = False)
##else:
##    print 'Already created', out
images = glob_find(to_dir, '_dem_mosaic.img')
for image in images:
    erdas_mosaicker(images, to_dir + 'big_dem.img', run = False)
#unchip(tifs, to_dir + 'unchip_test1.tif') 
#erdas_mosaicker(tifs, to_dir + '30m_geog_mosaic_test.img', run = False)
