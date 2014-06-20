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
def batch_read(in_images, out_queue):
    #global i
    print 'Starting worker'
    for image in in_images:
        print image
        b = brick(image,'',500,500,300,300,[6,4,3])
        out_queue.put(image)
        numpy.amin(b, axis = 0)
        print image
        b = None
        #i2 += 1
    print 'Finished worker'

if __name__ == '__main__':
    t1 = time.time()
    image_sets = set_maker(images,8)
    out_queue = multiprocessing.Queue()
    workers =[multiprocessing.Process(target = batch_read, args = (image_set, out_queue)) for image_set in image_sets]
    print workers
    for work in workers: work.start()
    for work in workers: work.join()
##    i = 1
##    p_list = []
##    for image_set in image_sets:
##        p_name = 'p' + str(i)
##        p_list.append(p_name)
##        exec(p_name+ ' = multiprocessing.Process(target=batch_read, args = (image_set,))')
##
##
####    print 'BEFORE:', p, p.is_alive()
##        exec(p_name + '.daemon = False')
####
##        exec(p_name + '.start()')
##        i += 1
####    #print 'DURING:', p, p.is_alive()
####    #p.join()
####
####    p = multiprocessing.Process(target=batch_read, args = (images[:8],))
####    #print 'BEFORE:', p2, p2.is_alive()
####    p.daemon = False
####    p.start()
####    #print 'DURING:', p2, p2.is_alive()
####    #p.terminate()
####    #print 'TERMINATED:', p, p.is_alive()
####
####    #p.join()
####    #p.join()
##    for p in p_list:
##        call = p + '.join()'
##        exec(call)
    t2 = time.time()
    print t1-t2
    for j in range(len(workers)):
        print out_queue.get()
    print
    print
    for image_set in image_sets:
        print image_set[0]
    #print 'JOINED:', p, p.is_alive()
#print i2