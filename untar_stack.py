from r_numpy_lib import *
######################################################
#Set up directories (will automatically create output dir if it does not exist)
tar_dir = 'X:/Landsat/169068/glovis/'
out_dir = 'X:/Landsat/169068/tar_test/'

#Provide extension ('.img' or '.tif' recommended)
output_extension = '.img'

#Can specify specific bands
#ex: bands 1, 2, and 3 would be bands = [0, 1, 2]
bands = []
######################################################
df = format_dict[output_extension]
check_dir(out_dir)
processing_dir = tar_dir
tars = glob(tar_dir, '.gz')
quick_look(tars, out_dir, bands = bands, df = df, out_extension = output_extension)

