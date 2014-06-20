"""Demonstrate the usage of numpy.memmap with joblib.Parallel

This example shows how to preallocate data in memmap arrays both for input and
output of the parallel worker processes.

Sample output for this program::

    [Worker 93486] Sum for row 0 is -1599.756454
    [Worker 93487] Sum for row 1 is -243.253165
    [Worker 93488] Sum for row 3 is 610.201883
    [Worker 93489] Sum for row 2 is 187.982005
    [Worker 93489] Sum for row 7 is 326.381617
    [Worker 93486] Sum for row 4 is 137.324438
    [Worker 93489] Sum for row 8 is -198.225809
    [Worker 93487] Sum for row 5 is -1062.852066
    [Worker 93488] Sum for row 6 is 1666.334107
    [Worker 93486] Sum for row 9 is -463.711714
    Expected sums computed in the parent process:
    [-1599.75645426  -243.25316471   187.98200458   610.20188337   137.32443803
     -1062.85206633  1666.33410715   326.38161713  -198.22580876  -463.71171369]
    Actual sums computed by the worker processes:
    [-1599.75645426  -243.25316471   187.98200458   610.20188337   137.32443803
     -1062.85206633  1666.33410715   326.38161713  -198.22580876  -463.71171369]

"""
##import tempfile
##import shutil
##import os
##import numpy as np
##
##from joblib import Parallel, delayed
##from joblib import load, dump
##
##
##def sum_row(input, output, i):
##    """Compute the sum of a row in input and store it in output"""
##    sum_ = input[i, :].sum()
##    print("[Worker %d] Sum for row %d is %f" % (os.getpid(), i, sum_))
##    output[i] = sum_
##
##if __name__ == "__main__":
##    rng = np.random.RandomState(42)
##    folder = tempfile.mkdtemp()
##    samples_name = os.path.join(folder, 'samples')
##    sums_name = os.path.join(folder, 'sums')
##    try:
##        # Generate some data and an allocate an output buffer
##        samples = rng.normal(size=(10, int(1e6)))
##
##        # Pre-allocate a writeable shared memory map as a container for the
##        # results of the parallel computation
##        sums = np.memmap(sums_name, dtype=samples.dtype,
##                         shape=samples.shape[0], mode='w+')
##
##        # Dump the input data to disk to free the memory
##        dump(samples, samples_name)
##
##        # Release the reference on the original in memory array and replace it
##        # by a reference to the memmap array so that the garbage collector can
##        # release the memory before forking. gc.collect() is internally called
##        # in Parallel just before forking.
##        samples = load(samples_name, mmap_mode='r')
##
##        # Fork the worker processes to perform computation concurrently
##        Parallel(n_jobs=4)(delayed(sum_row)(samples, sums, i)
##                           for i in range(samples.shape[0]))
##
##        # Compare the results from the output buffer with the ground truth
##        print("Expected sums computed in the parent process:")
##        expected_result = samples.sum(axis=1)
##        print(expected_result)
##
##
##        print("Actual sums computed by the worker processes:")
##        print(sums)
##
##        assert np.allclose(expected_result, sums)
##    finally:
##        try:
##            shutil.rmtree(folder)
##        except:
##            print("Failed to delete: " + folder)

##from r_numpy_lib import *
##import scipy.misc,numexpr
##image = 'R:/NAFD3/timesync_setup/imagery/3532/refls/w2p035r032_a1994cmp_ev.img'
##b = brick(image,'',2000,2000,500,500, band_list = [6,4,3])
##a = brick(image,'',3000,3000,500,500, band_list = [6,4,3])
##scipy.misc.imsave(image + '.jpg',b)
##t1 = time.time()
###eval('numpy.diff(a)')
##numexpr.evaluate('numpy.diff(a)')
##t2 = time.time()
##print t2-t1
##b = None
##a = None
#######################################################################
# This script compares the speed of the computation of a polynomial
# for different (numpy and numexpr) in-memory paradigms.
#
# Author: Francesc Alted
# Date: 2010-10-01
#######################################################################

##from time import time
##import numpy as np
##import numexpr
##
##
##expr = ".25*x**3 + .75*x**2 - 1.5*x - 2"  # the polynomial to compute
###expr = "((.25*x + .75)*x - 1.5)*x - 2"   # a computer-friendly polynomial
###expr = "sin(x)**2+cos(x)**2"             # a transcendental function
##N = 10*1000*1000            # the number of points to compute expression
##x = np.linspace(-1, 1, N)   # the x in range [-1, 1]
##
###what = "numpy"              # uses numpy for computations
##what = "numexpr"           # uses numexpr for computations
##
##numexpr.set_num_threads(1)       # the number of threads for numexpr computations
##
##def compute():
##    """Compute the polynomial."""
##    global expr
##    if what == "numpy":
##        if "sin" in expr:
##            # Trick to allow numpy evaluate this
##            expr = "np.sin(x)**2+np.cos(x)**2"
##        y = eval(expr)
##    else:
##        y = numexpr.evaluate(expr)
##    return len(y)
##
##
####if __name__ == '__main__':
##print "Computing: '%s' using %s with %d points" % (expr, what, N)
##t0 = time()
##result = compute()
##ts = round(time() - t0, 3)
##print "*** Time elapsed:", ts
from multiprocessing import Pool

def f(x):
    return x*x

if __name__ == '__main__':
    pool = Pool(processes=4)              # start 4 worker processes

    result = pool.apply_async(f, (10,))    # evaluate "f(10)" asynchronously
    print result.get(timeout=1)           # prints "100" unless your computer is *very* slow

##    print pool.map(f, range(10))          # prints "[0, 1, 4,..., 81]"
##
##    it = pool.imap(f, range(10))
##    print it.next()                       # prints "0"
##    print it.next()                       # prints "1"
##    print it.next(timeout=1)              # prints "4" unless your computer is *very* slow
##
##    import time
##    result = pool.apply_async(time.sleep, (10,))
##    print result.get(timeout=1)           # raises TimeoutError