from multiprocessing import Pool
#import sys, os
#tools_dir = 'O:/03_Process/Tools/'
#sys.path.append(tools_dir)
from r_numpy_lib import *
###################################
import multiprocessing
import time

image_dir = 'R:/NAFD3/timesync_setup/imagery/1637/refls/'
images = glob(image_dir, '.img')
#i2 = 0
def batch_read(in_images):
    #global i
    print 'Starting worker'
    out_list = {}
    for image in in_images:
        print image
        b = brick(image,'',2500,2500,300,300,[6,4,3])
        #out_queue.put(image)
        numpy.amin(b, axis = 0)
        print image
        out_list[image] = b
        b = None
        #i2 += 1
    return out_list
    print 'Finished worker'
if __name__ == '__main__':
    t1 = time.time()
    image_sets = set_maker(images,8)
    pool = Pool(processes=8)
    out_images = pool.map(batch_read, image_sets)
    for ois in out_images:
        for oi in ois:
            print oi,ois[oi]
    t2 = time.time()
    print t1-t2
