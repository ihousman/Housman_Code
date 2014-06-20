from r_numpy_lib import *
import scipy.misc

in_folder = 'R:/NAFD3/timesync_setup/imagery/3532/refls/'
out_folder = in_folder + 'jpgs/'
images = glob(in_folder, '.img')
check_dir(out_folder)
xo_list = random.sample(range(1000,2000),50)
yo_list = random.sample(range(1000,2000),50)
xo_yo_list = transpose([xo_list,yo_list])
w = 2500
h = 2000
n_std = 2.
aspect_ratio = 2
widths = [20,50,100,300,500,1000]
for image in images[:1]:
    for xo,yo in xo_yo_list:

        for w in widths:
            h = w /aspect_ratio
            ulx = int(xo - (w/2.))
            uly = int(yo - (h/2.))
            out_jpg = out_folder + base(image) + '_' + str(xo) + '_' + str(yo) + '_' + str(w) + '_' + str(h) + '.jpg'
            if os.path.exists(out_jpg) == True:
                b = scipy.misc.imread(out_jpg)
            else:
                b = brick(image,'',ulx,uly,w,h, band_list = [6,4,3])
                b =scipy.misc.bytescale(b,1)
                scipy.misc.imsave(out_jpg,b)

